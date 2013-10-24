# -*- coding: utf-8 -*-
from django.http.response import Http404
from clients_support.conf import settings

from clients_support.models import Ticket, Message, StatusLog, TicketType, Tag
from rest_framework.authentication import SessionAuthentication
from rest_framework import viewsets, permissions
from django.db.models import Q
from clients_support.serializers import TicketSerializer, MessageSerializer


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


class TicketViewSet(viewsets.ModelViewSet):

    model = Ticket
    permission_classes = (TicketPermissions, )
    authentication_classes = (UnsafeSessionAuthentication, )
    model_serializer_class = TicketSerializer

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

        if not allow_guest:
            qs.filter(user__exists=True)
        #if publish == 'true':
        #    queryset = queryset.filter(publish=True)
        if current_user == 'true':
            qs = qs.filter(user=user)
        elif current_user == 'false':
            qs = qs.exclude(user=user)
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


class MessagePermissions(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return True


class MessageViewSet(viewsets.ModelViewSet):
    model = Message
    authentication_classes = (UnsafeSessionAuthentication,)
    model_serializer_class = MessageSerializer

    @property
    def queryset(self):
        try:
            ticket = int(self.request.QUERY_PARAMS.get('ticket', None))
        except (ValueError, TypeError):
            ticket = None
        queryset = Message.objects.all()
        if ticket:
            queryset = queryset.filter(ticket_id=ticket)
        return queryset

    def pre_save(self, obj):
        """
        Set the object's owner, based on the incoming request.
        """
        obj.user = self.request.user


class TicketTypeViewSet(viewsets.ModelViewSet):
    model = TicketType