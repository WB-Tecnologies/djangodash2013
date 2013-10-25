# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta
from django import template
from clients_support.conf import settings

from clients_support.models import Ticket

register = template.Library()

date_params = lambda n, _date: {n+'__year': _date.year, n+'__month': _date.month, n+'__day': _date.day}


@register.inclusion_tag('clients_support/admin/block_with_statistics.html')
def block_with_statistics():
    if not settings.ADMIN_SHOW_BLOCK_STATISTICS:
        return dict(show_statistics=False)
    today = datetime.now().today()
    queryset = Ticket.objects.all()

    return dict(
        show_statistics=True,
        closed_count=queryset.filter(status=Ticket.CLOSED_STATUS).count(),
        open_count=queryset.exclude(status__in=[Ticket.CLOSED_STATUS, Ticket.SOLVED_STATUS]).count(),
        total_count=queryset.count(),
        add_today_count=queryset.filter(**date_params('created_at', today)).count(),
        closed_today_count=queryset.filter(status=Ticket.CLOSED_STATUS, **date_params('closed_at', today)).count()
    )
