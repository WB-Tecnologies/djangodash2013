from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _


class Ticket(models.Model):

    NEW_STATUS = 'new'
    READ_STATUS = 'read'
    ASSIGNED_STATUS = 'assigned'
    SOLVED_STATUS = 'solved'
    CLOSED_STATUS = 'closed'
    REOPENED_STATUS = 'reopened'

    STATUSES = (
        (NEW_STATUS, _('New ticket')),
        (READ_STATUS, _('Ticket was read')),
        (ASSIGNED_STATUS, _('Ticket was assigned')),
        (SOLVED_STATUS, _('Ticket was solved')),
        (CLOSED_STATUS, _('Ticket was closed')),
        (REOPENED_STATUS, _('Ticket was reopened'))
    )

    SATISFIED_MARK = 'satisfied'
    NOT_SATISFIED_MARK = 'not_satisfied'
    NOT_RATED_MARK = 'not_rated'

    MARKS = (
        (SATISFIED_MARK, _('User was satisfied')),
        (NOT_SATISFIED_MARK, _('User was not satisfied')),
        (NOT_RATED_MARK, _('User is not rated ticket'))
    )

    HIGH_IMPORTANT = 'high'
    NORMAL_IMPORTANT = 'normal'
    NOT_IMPORTANT = 'not'

    IMPORTANCE = (
        (HIGH_IMPORTANT, _('High importance')),
        (NORMAL_IMPORTANT, _('Normal importance')),
        (NOT_IMPORTANT, _('Not important'))
    )

    subject = models.CharField(_('Subject'), max_length=255)
    text = models.TextField(_('Text'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name=_('User'))
    guest_name = models.CharField(_('Guest name'), max_length=255, blank=True, null=True)
    guest_email = models.CharField(_('Guest email'), max_length=255, blank=True, null=True)
    status = models.CharField(_('Status'), max_length=10, choices=STATUSES)
    user_mark = models.CharField(_('User mark'), max_length=15, choices=MARKS)
    type = models.ForeignKey(TicketType, verbose_name=_('Ticket type'))
    importance = models.CharField(_('Importance'), max_length=10, choices=IMPORTANCE)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name=_('Manager'))
    tags = models.ManyToManyField(Tag, verbose_name=_('Tags'))
    # Used to create a secret link (for guests)
    secret_code = models.URLField(_('Secret code (for guests)'))
    # Publish a ticket to be seen by other users
    publish = models.BooleanField(_('Publish ticket'))
    # Viewed after close
    viewed = models.BooleanField(_('Was viewed after close'))
    created_time = models.DateTimeField(_('Created time'), auto_now_add=True)
    updated_time = models.DateTimeField(_('Last updated time'), auto_now=True)
    closed_time = models.DateTimeField(_('Closed time'), blank=True, null=True)

    def __unicode__(self):
        return self.subject


class Message(models.Model):
    ticket = models.ForeignKey(Ticket, verbose_name=_('Ticket'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name=_('User'))
    # Sended from guest
    from_guest = models.BooleanField(_('Message from guest'))
    text = models.TextField(_('Text'))
    # If a message is created by the client, then automatically placed in the True, otherwise False.
    was_read = models.BooleanField(_('Message was read'))
    created_time = models.DateTimeField(_('Created time'), auto_now_add=True)

    def __unicode__(self):
        return str(self.ticket)


class TicketType(models.Model):
    name = models.CharField(_('Name'), max_length=255)

    def __unicode__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(_('Name'), max_length=255)

    def __unicode__(self):
        return self.name


class StatusLog(models.Model):
    ticket = models.ForeignKey(Ticket, verbose_name=_('Ticket'))
    # User who changed status
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name=_('User'))
    status = models.CharField(_('Status'), max_length=10, choices=Ticket.STATUSES)
    # Time when the status was changed
    created_time = models.DateTimeField(_('Time when the status was changed'), auto_now_add=True)

    def __unicode__(self):
        return str(self.ticket)