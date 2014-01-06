# -*- coding: utf-8 -*-

from optparse import make_option
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from clients_support import get_package_name

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _, activate, deactivate
from django.conf import settings as django_settings
from clients_support.models import Ticket, Message, Tag, TicketType, StatusLog


SUPPORT_PERMISSIONS = (
    ('actions_make_published', _('Can publish tickets')),
    ('actions_change_importance', _('Can change importance tickets')),
    ('actions_change_status', _('Can change status tickets')),
    ('take_ticket_process', _('Can take the ticket for processing')),
)


class Command(BaseCommand):
    """
    Command add groups and permissions (including custom) for clients_support
    """

    can_import_settings = True
    help = 'Set group and permissions by %s' % get_package_name()
    option_list = BaseCommand.option_list + (
        make_option('--ignore_language_code', '--ilc',
                    action='store_true',
                    dest='ignore_lang',
                    default=False,
                    help='Ignore the language of the draft in the names of custom permissions.'),
    )

    def handle(self, *args, **options):
        ignore_lang = options.get('ignore_lang', False)

        if not ignore_lang:
            # activate the language
            activate(django_settings.LANGUAGE_CODE)

        group_name = lambda name: '%s_%s' % (get_package_name(), name)

        content_type = ContentType.objects.get_for_model(Ticket)
        sm_group, smg_created = Group.objects.get_or_create(name=group_name('supermanager'))
        m_group, mg_created = Group.objects.get_or_create(name=group_name('manager'))

        sm_perm_list = []

        for codename, desc in SUPPORT_PERMISSIONS:
            permission, is_created = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
                defaults=dict(name=desc)
            )
            if not is_created:
                permission.name = desc
                permission.save()
            m_group.permissions.add(permission)
            sm_group.permissions.add(permission)
            sm_perm_list.append(codename)

        def set_other_permissions(group, types):
            for permission in Permission.objects \
                .filter(content_type__in=types.values()) \
                .exclude(codename__in=sm_perm_list):
                group.permissions.add(permission)

        set_other_permissions(sm_group, ContentType.objects.get_for_models(Ticket, Message, TicketType, Tag, StatusLog))
        set_other_permissions(m_group, ContentType.objects.get_for_models(Ticket, Message))

        if not ignore_lang:
            # deactivate the language
            deactivate()