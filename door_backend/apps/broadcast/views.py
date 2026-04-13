from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import BroadcastChannel, BroadcastMessage, BroadcastSubscription, BroadcastDelivery
from .serializers import (
    BroadcastChannelSerializer,
    BroadcastMessageSerializer,
    BroadcastDeliverySerializer,
    BroadcastDeliveryStatusUpdateSerializer,
)
from .services import BroadcastDeliveryService
from .tasks import send_broadcast_message


class BroadcastChannelViewSet(viewsets.ModelViewSet):
    serializer_class = BroadcastChannelSerializer
    filterset_fields = ["organization", "group", "interaction", "type", "is_active"]

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
    filterset_fields = ["channel", "interaction", "type", "status"]

    def get_queryset(self):
        return BroadcastMessage.objects.filter(
            channel__organization__members__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        channel = BroadcastChannel.objects.get(pk=self.request.data.get("channel"))
        interaction = serializer.validated_data.get("interaction") or channel.interaction
        msg = serializer.save(sender=self.request.user, interaction=interaction)
        send_broadcast_message.delay(str(msg.id))

    @action(detail=True, methods=["post"], url_path="dispatch")
    def dispatch_message(self, request, pk=None):
        message = self.get_object()
        send_broadcast_message(str(message.id))
        message.refresh_from_db()
        return Response(BroadcastMessageSerializer(message).data)

    @action(detail=True, methods=["post"], url_path="delivery-status")
    def delivery_status(self, request, pk=None):
        message = self.get_object()
        serializer = BroadcastDeliveryStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        delivery = BroadcastDelivery.objects.get(
            pk=request.data.get("delivery_id"),
            message=message,
            user=request.user,
        )
        if serializer.validated_data["status"] == "seen":
            BroadcastDeliveryService.mark_seen(delivery)
        elif serializer.validated_data["status"] == "delivered":
            BroadcastDeliveryService.mark_delivered(delivery)
        else:
            delivery.status = serializer.validated_data["status"]
            delivery.save(update_fields=["status", "updated_at_server"])
        delivery.refresh_from_db()
        return Response(BroadcastDeliverySerializer(delivery).data)
