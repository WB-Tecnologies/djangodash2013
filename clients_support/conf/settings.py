# -*- coding: utf-8 -*-

from django.conf import settings as django_settings
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _


ALLOW_GUEST_SUPPORT = getattr(django_settings, 'SUPPORT_ALLOW_GUEST', True)

ADMIN_SHOW_BLOCK_STATISTICS = getattr(django_settings, 'SUPPORT_ADMIN_SHOW_STATISTICS', True)

ADMIN_PERMISSION_ADD_TICKET = getattr(django_settings, 'SUPPORT_ADMIN_PERMISSION_ADD_TICKET', False)

INCLUDE_AUTOCOMPLETE_LIGHT_URLS = getattr(django_settings, 'SUPPORT_INCLUDE_AUTOCOMPLETE_LIGHT_URLS', True)

ADMIN_SHOW_USER_HISTORY_TICKETS = getattr(django_settings, 'SUPPORT_ADMIN_SHOW_USER_HISTORY_TICKETS', True)

AUTH_USER_MODEL = getattr(django_settings, 'AUTH_USER_MODEL', 'auth.User')

PROJECT_DATE_FORMAT = getattr(django_settings, 'SUPPORT_DATE_FORMAT', "%B %d, %Y; %H:%M")