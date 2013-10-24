# -*- coding: utf-8 -*-
from django.core.validators import RegexValidator
from django.template.defaultfilters import striptags
import re
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.utils.translation import ugettext_lazy as _

guest_name_validator = RegexValidator(
    re.compile(r'(\S\s*){3,}'),
    _('Enter at least three characters.'),
    'invalid_guest_name'
)


class TicketSerializer(ModelSerializer):

    guest_name = serializers.CharField(min_length=3, max_length=50, validators=[guest_name_validator])
    guest_email = serializers.EmailField(max_length=255)

    def __init__(self, *args, **kwargs):
        super(TicketSerializer, self).__init__(*args, **kwargs)
        request = kwargs['context']['request']
        if request.user.is_authenticated():
            for name in ['guest_name', 'guest_email']:
                self.fields[name].required = False

    def clean_guest_name(self, value):
        return value.strip()

    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        ret = self._dict_class()
        ret.fields = self._dict_class()
        ret.empty = obj is None

        for field_name, field in self.fields.items():
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            if field_name in ['subject', 'text']:
                value = striptags(value)
            ret[key] = value
            ret.fields[key] = field
        return ret


class MessageSerializer(ModelSerializer):

    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        ret = self._dict_class()
        ret.fields = self._dict_class()
        ret.empty = obj is None

        for field_name, field in self.fields.items():
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            if field_name == 'text':
                value = striptags(value)
            ret[key] = value
            ret.fields[key] = field
        return ret


