# -*- coding: utf-8 -*-


def get_version():
    return '0.0.2'


def get_package_name():
    return __name__


def get_package_permission(name):
    return '%s.%s' % (__name__, name)