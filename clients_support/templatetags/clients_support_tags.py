# -*- coding: utf-8 -*-

from datetime import datetime
from django import template
from clients_support.conf import settings
from clients_support.helpers import perm_name

from clients_support.models import Ticket

register = template.Library()

date_params = lambda n, _date: {n + '__year': _date.year, n + '__month': _date.month, n + '__day': _date.day}


@register.inclusion_tag('clients_support/admin/block_with_statistics.html')
def block_with_statistics():
    if not settings.ADMIN_SHOW_BLOCK_STATISTICS:
        return dict(show_statistics=False)
    today = datetime.now().today()
    queryset = Ticket.objects.all()
    closed_queryset = queryset.filter(status=Ticket.CLOSED_STATUS)

    return dict(
        show_statistics=True,
        closed_count=closed_queryset.count(),
        open_count=queryset.exclude(status__in=[Ticket.CLOSED_STATUS, Ticket.SOLVED_STATUS]).count(),
        total_count=queryset.count(),
        add_today_count=queryset.filter(**date_params('created_at', today)).count(),
        closed_today_count=closed_queryset.filter(**date_params('closed_at', today)).count()
    )


@register.inclusion_tag('clients_support/admin/ticket_process_line.html', takes_context=True)
def ticket_process_line(context):
    user = context.get('user')
    ticket_id = context.get('object_id', 0)
    show_ticket_process = False
    if Ticket.objects.filter(manager=None, pk=ticket_id).count():
        show_ticket_process = user.has_perm(perm_name('take_ticket_process'))
    return dict(
        show_ticket_process=show_ticket_process,
    )
