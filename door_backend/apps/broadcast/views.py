from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import BroadcastChannel, BroadcastMessage, BroadcastSubscription
from .serializers import BroadcastChannelSerializer, BroadcastMessageSerializer
from .tasks import send_broadcast_message


class BroadcastChannelViewSet(viewsets.ModelViewSet):
    serializer_class = BroadcastChannelSerializer
    filterset_fields = ["organization", "type", "is_active"]

    def get_queryset(self):
        return BroadcastChannel.objects.filter(
            organization__members__user=self.request.user
        ).distinct()

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk=None):
        channel = self.get_object()
        BroadcastSubscription.objects.get_or_create(channel=channel, user=request.user)
        return Response({"ok": True})

    @action(detail=True, methods=["post"])
    def unsubscribe(self, request, pk=None):
        channel = self.get_object()
        BroadcastSubscription.objects.filter(channel=channel, user=request.user).delete()
        return Response({"ok": True})


class BroadcastMessageViewSet(viewsets.ModelViewSet):
    serializer_class = BroadcastMessageSerializer
    filterset_fields = ["channel", "type"]

    def get_queryset(self):
        return BroadcastMessage.objects.filter(
            channel__organization__members__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        msg = serializer.save(sender=self.request.user)
        send_broadcast_message.delay(str(msg.id))
