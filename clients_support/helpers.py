# -*- coding: utf-8 -*-
import locale
from django.utils.translation import get_language, gettext, to_locale
from clients_support import get_package_name


def set_project_locale():
    try:
        locale.setlocale(locale.LC_TIME, (to_locale(get_language()), 'UTF-8'))
    except:
        pass


def perm_name(name):
    return '%s.%s' % (get_package_name(), name)
