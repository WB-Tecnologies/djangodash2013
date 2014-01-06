# -*- coding: utf-8 -*-
from datetime import datetime
import autocomplete_light
from django import forms
from django.contrib import admin, messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _, ungettext
from clients_support import get_package_permission
from clients_support.conf import settings

from clients_support.models import Ticket, TicketType, StatusLog, Tag, Message


def get_admin_url(obj):
    content_type = ContentType.objects.get_for_model(obj.__class__)
    return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(obj.pk,))


class AssignManagerFilter(admin.SimpleListFilter):
    title = _('Only my tickets')

    parameter_name = 'assign_manager'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.filter(manager=request.user)
        elif value == 'no':
            return queryset.exclude(manager=request.user)
        return queryset


class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['status'].choices = \
                self.instance.get_status_choices_specific([Ticket.REOPENED_STATUS]) if self.instance.is_solved else \
                self.instance.get_status_choices_unless([Ticket.SOLVED_STATUS, Ticket.REOPENED_STATUS])


class MessageAdminInline(admin.TabularInline):

    model = Message
    extra = 1


class TicketAdmin(admin.ModelAdmin):

    PERMISSION_ACTIONS = SortedDict((
        ('actions_make_published', ['make_published']),
        ('actions_change_importance', ['change_importance_to_high',
                                       'change_importance_to_normal',
                                       'change_importance_to_low']),
        ('actions_change_status', ['change_status_to_read', 'change_status_to_closed'])
    ))

    form = autocomplete_light.modelform_factory(Ticket, form=TicketForm)

    inlines = [MessageAdminInline]

    list_display = ('id', '_subject', 'user', 'manager', 'status', 'type', 'importance', 'publish', 'updated_at')
    list_filter = ('tags', 'type', 'importance', 'status', 'created_at', AssignManagerFilter)
    search_fields = ('subject', 'text')

    actions = sum(PERMISSION_ACTIONS.values(), [])

    change_form_template = 'clients_support/admin/change_ticket.html'
    change_list_template = 'clients_support/admin/change_list.html'
    readonly_fields = ('user_mark', 'user', 'manager', 'created_at', 'closed_at')

    def get_actions(self, request):
        actions = super(TicketAdmin, self).get_actions(request)

        for name, part in self.PERMISSION_ACTIONS.items():
            if not request.user.has_perm(get_package_permission(name)):
                for action in part:
                    del actions[action]

        return actions

    def _subject(self, obj):
        return u'<a href="%s">%s</a>' % (get_admin_url(obj), obj.subject)
    _subject.allow_tags = True
    _subject.short_description = _('Subject')

    def has_add_permission(self, request):
        return settings.ADMIN_PERMISSION_ADD_TICKET

    def response_change(self, request, obj):
        if '_ticket_process' in request.POST:
            msg = _('uyctuk.')
            self.message_user(request, msg)
            return HttpResponseRedirect(request.path)
        return super(TicketAdmin, self).response_change(request, obj)

    def save_model(self, request, obj, form, change):
        if '_ticket_process' in request.POST:
            obj.manager = request.user
        obj.save()
        if 'status' in form.changed_data:
            StatusLog.add_log(obj, request.user, obj.status)

    def make_published(self, request, queryset):
        count = queryset.exclude(publish=True).update(publish=True)
        messages.success(request, ungettext(
            'Published %(count)d ticket.',
            'Published %(count)d tickets.',
            count) % dict(count=count)
        )
    make_published.short_description = _('Mark selected tickets as published')

    def _change_importance(self, request, queryset, value):
        count = queryset.exclude(importance=value).update(importance=value)
        messages.success(request, ungettext(
            'Importance `%(value)s` put %(count)d ticket.',
            'Importance `%(value)s` put %(count)d tickets.',
            count) % dict(value=value, count=count)
        )

    def change_importance_to_high(self, request, queryset):
        self._change_importance(request, queryset, Ticket.HIGH_IMPORTANT)
    change_importance_to_high.short_description = _('Change the importance of the selected tickets on a high')

    def change_importance_to_normal(self, request, queryset):
        self._change_importance(request, queryset, Ticket.NORMAL_IMPORTANT)
    change_importance_to_normal.short_description = _('Change the importance of the selected tickets on a normal')

    def change_importance_to_low(self, request, queryset):
        self._change_importance(request, queryset, Ticket.NOT_IMPORTANT)
    change_importance_to_low.short_description = _('Change the importance of the selected tickets on a low')

    def change_status_to_read(self, request, queryset):
        for ticket in queryset:
            if ticket.status == Ticket.NEW_STATUS:
                StatusLog.add_log(ticket, request.user, ticket.READ_STATUS)
        count = queryset.filter(status=Ticket.NEW_STATUS).update(status=Ticket.READ_STATUS)
        if count:
            messages.success(request, ungettext(
                'Status `read` put %(count)d ticket.',
                'Status `read` put %(count)d tickets.',
                count) % dict(count=count))
        else:
            messages.error(request, _('Status `read` can be supplied only by a new tickets.'))

    change_status_to_read.short_description = _('Change the status of the selected tickets as read')

    def change_status_to_closed(self, request, queryset):
        deny_statuses = [Ticket.CLOSED_STATUS, Ticket.SOLVED_STATUS, Ticket.REOPENED_STATUS]
        for ticket in queryset:
            if not ticket.status in deny_statuses:
                StatusLog.add_log(ticket, request.user, ticket.CLOSED_STATUS)
        count = queryset.exclude(status__in=deny_statuses).\
            update(status=Ticket.CLOSED_STATUS, closed_at=datetime.now())
        if count:
            messages.success(request, ungettext(
                'Status `closed` put %(count)d ticket.',
                'Status `closed` put %(count)d tickets.',
                count) % dict(count=count))
        else:
            messages.error(request, _('Status `closed` can not be put tickets by status '
                                      '%(statuses)s.') % dict(statuses=', '.join(deny_statuses)))

    change_status_to_closed.short_description = _('Change the status of the selected tickets as closed')


class StatusLogAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'status', 'created_at')
    list_filter = ('ticket', 'user', 'status', 'created_at')
    readonly_fields = ('ticket', 'user', 'status')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False


admin.site.register(Tag)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(StatusLog, StatusLogAdmin)
admin.site.register(TicketType)