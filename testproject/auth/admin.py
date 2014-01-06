# -*- coding: utf-8 -*-

import django.contrib.auth.models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from auth.models import User


# Now register the new UserAdmin...
admin.site.unregister(django.contrib.auth.models.User)
admin.site.register(User, UserAdmin)