# -*- coding: utf-8 -*-
from django.http.response import Http404
import operator
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from clients_support.conf import settings

from clients_support.models import Ticket, Message, StatusLog, TicketType, Tag
from rest_framework.authentication import SessionAuthentication
from rest_framework import viewsets, permissions
from django.db.models import Q
from clients_support.serializers import TicketSerializer, MessageSerializer
from django.utils.translation import pgettext_lazy


class UnsafeSessionAuthentication(SessionAuthentication):

    def authenticate(self, request):
        http_request = request._request
        user = getattr(http_request, 'user', None)

        if not user or not user.is_active:
           return None

        return user, None


class TicketPermissions(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ['DELETE', 'PUT']:
            return False
        is_owner = obj.user == request.user
        if (request.method == 'POST') and obj.user and (not is_owner):
            return False
        return is_owner or obj.publish


class TicketJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context and isinstance(data, dict):
            data['page_size'] = renderer_context['view'].paginate_by
            data['previous'] = pgettext_lazy('pager_prev', 'Prev')
            data['next'] = pgettext_lazy('pager_next', 'Next')
        return super(TicketJSONRenderer, self).render(data, accepted_media_type, renderer_context)


class TicketViewSet(viewsets.ModelViewSet):

    model = Ticket
    permission_classes = (TicketPermissions, )
    authentication_classes = (UnsafeSessionAuthentication, )
    model_serializer_class = TicketSerializer
    renderer_classes = ( TicketJSONRenderer, BrowsableAPIRenderer)

    paginate_by = settings.TICKETS_PAGINATE_BY
    paginate_by_param = 'page_size'
    max_paginate_by = 100

    @property
    def queryset(self):
        qs = Ticket.objects.filter(publish=True)

        user = self.request.user
        is_guest = user.is_anonymous()
        allow_guest = settings.ALLOW_GUEST_SUPPORT

        if is_guest:
            user = None
            if not allow_guest:
                return qs.none()

        publish = self.request.QUERY_PARAMS.get('publish', None)
        current_user = self.request.QUERY_PARAMS.get('current_user', None)
        term = self.request.QUERY_PARAMS.get('term', '')

        if not allow_guest:
            qs.filter(user__exists=True)
        #if publish == 'true':
        #    queryset = queryset.filter(publish=True)
        if current_user == 'true':
            qs = qs.filter(user=user)
        elif current_user == 'false' and user:
            qs = qs.exclude(user=user)

        if term:
            # generate search queries, example: Q(subject__icontains=term)
            _pfx = '__%scontains' % settings.SEARCH_I
            q_search = [Q((field_name + _pfx, term))
                              for field_name in settings.SEARCH_FIELDS]
            qs = qs.filter(reduce(operator.or_, q_search))
        return qs

    def paginate_queryset(self, queryset, page_size=None):
        current_user = self.request.QUERY_PARAMS.get('current_user', None)
        if current_user == 'true':
            return
        return super(TicketViewSet, self).paginate_queryset(queryset, page_size=None)

    def pre_save(self, obj):
        """
        Set the object's owner, based on the incoming request.
        """
        user = self.request.user
        is_guest = user.is_anonymous()
        allow_guest = settings.ALLOW_GUEST_SUPPORT

        if is_guest and not allow_guest:
            raise Http404

        obj.user = None if is_guest else user


class MessagePermissions(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return True


class MessageViewSet(viewsets.ModelViewSet):
    model = Message
    authentication_classes = (UnsafeSessionAuthentication,)
    model_serializer_class = MessageSerializer

    @property
    def queryset(self):
        ticket_id = self.request.QUERY_PARAMS.get('ticket', '')
        qs = Message.objects.all()
        if ticket_id.isdigit():
            qs = qs.filter(ticket__id=ticket_id)
        else:
            qs = qs.none()
        return qs

    def pre_save(self, obj):
        """
        Set the object's owner, based on the incoming request.
        """
        user = self.request.user
        is_guest = user.is_anonymous()
        allow_guest = settings.ALLOW_GUEST_SUPPORT

        if is_guest and not allow_guest:
            raise Http404

        obj.user = None if is_guest else user


class TicketTypeViewSet(viewsets.ModelViewSet):
    model = TicketType