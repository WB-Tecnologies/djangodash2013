# -*- coding: utf-8 -*-

from django.conf import settings as django_settings

ALLOW_GUEST_SUPPORT = getattr(django_settings, 'SUPPORT_ALLOW_GUEST', True)

ADMIN_SHOW_BLOCK_STATISTICS = getattr(django_settings, 'SUPPORT_ADMIN_SHOW_STATISTICS', True)

ADMIN_PERMISSION_ADD_TICKET = getattr(django_settings, 'SUPPORT_ADMIN_PERMISSION_ADD_TICKET', False)

INCLUDE_AUTOCOMPLETE_LIGHT_URLS = getattr(django_settings, 'SUPPORT_INCLUDE_AUTOCOMPLETE_LIGHT_URLS', True)

ADMIN_SHOW_USER_HISTORY_TICKETS = getattr(django_settings, 'SUPPORT_ADMIN_SHOW_USER_HISTORY_TICKETS', True)

AUTH_USER_MODEL = getattr(django_settings, 'AUTH_USER_MODEL', 'auth.User')

PROJECT_DATE_FORMAT = getattr(django_settings, 'SUPPORT_DATE_FORMAT', "%B %d, %Y; %H:%M")

SEARCH_FIELDS = getattr(django_settings, 'SUPPORT_SEARCH_FIELDS', ['subject'])

SEARCH_I = '' if getattr(django_settings, 'SUPPORT_SEARCH_CASE_SENSITIVE', False) else 'i'

ALLOW_TICKET_FIELDS = getattr(
    django_settings,
    'SUPPORT_ALLOW_AJAX_TICKET_FIELDS',
    [
        'id', 'subject', 'text', 'created_at',
        'guest_name', 'user', 'status', 'user_mark',
        'type', 'importance', 'viewed', 'tags'
    ]
)

TICKETS_PAGINATE_BY = getattr(django_settings, 'SUPPORT_PAGINATE_BY', 8)

TICKET_MIN_LENGTH = getattr(django_settings, 'SUPPORT_TICKET_MIN_LENGTH', 50)

# if set None then maximum length for TEXT field types
TICKET_MAX_LENGTH = getattr(django_settings, 'SUPPORT_TICKET_MAX_LENGTH', None)

MESSAGE_MIN_LENGTH = getattr(django_settings, 'SUPPORT_MESSAGE_MIN_LENGTH', 3)

# if set None then maximum length for TEXT field types
MESSAGE_MAX_LENGTH = getattr(django_settings, 'SUPPORT_MESSAGE_MAX_LENGTH', None)


