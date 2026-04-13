import json
import uuid
from datetime import datetime, timezone

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class BroadcastConsumer(AsyncWebsocketConsumer):
    """
    Phase-1 Broadcast WebSocket contract.

    URL:
      ws://host/ws/broadcast/<channel_id>/?token=<jwt>

    Client -> Server events:
      - broadcast.ack   { delivery_id }
      - broadcast.seen  { delivery_id }
      - ping

    Server -> Client events:
      - broadcast.connected
      - broadcast.message
      - broadcast.status
      - ack
      - error
    """

    async def connect(self):
        self.channel_id = self.scope["url_route"]["kwargs"]["channel_id"]
        self.group_name = f"broadcast_{self.channel_id}"
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        if not await self._can_access_channel():
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        context = await self._channel_context()
        await self._send_event("broadcast.connected", {"channel_id": self.channel_id, **context})

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            payload = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            await self._send_error("bad_json", "Invalid JSON payload.")
            return

        event_type = payload.get("type")
        request_id = payload.get("request_id") or str(uuid.uuid4())

        if event_type == "broadcast.ack":
            delivery_id = payload.get("delivery_id")
            if not delivery_id:
                await self._send_error("delivery_id_required", "delivery_id is required.", request_id=request_id)
                return
            await self._mark_delivered(delivery_id)
            await self._send_ack("broadcast.ack", request_id=request_id)
            return

        if event_type == "broadcast.seen":
            delivery_id = payload.get("delivery_id")
            if not delivery_id:
                await self._send_error("delivery_id_required", "delivery_id is required.", request_id=request_id)
                return
            updated = await self._mark_seen(delivery_id)
            if updated:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "ws_event",
                        "event": "broadcast.status",
                        "data": updated,
                    },
                )
            await self._send_ack("broadcast.seen", request_id=request_id)
            return

        if event_type == "ping":
            await self._send_event("pong", {"channel_id": self.channel_id}, request_id=request_id)
            return

        await self._send_error("unknown_event", f"Unsupported event '{event_type}'.", request_id=request_id)

    async def ws_event(self, event):
        await self._send_event(event.get("event", "unknown"), event.get("data", {}), request_id=event.get("request_id"))

    async def broadcast_message(self, event):
        await self._send_event("broadcast.message", event.get("data", {}))

    async def _send_event(self, event: str, data: dict, request_id: str | None = None):
        await self.send(
            json.dumps(
                {
                    "event": event,
                    "ok": True,
                    "request_id": request_id,
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "data": data,
                }
            )
        )

    async def _send_ack(self, action: str, request_id: str | None = None):
        await self._send_event("ack", {"action": action}, request_id=request_id)

    async def _send_error(self, code: str, message: str, request_id: str | None = None):
        await self.send(
            json.dumps(
                {
                    "event": "error",
                    "ok": False,
                    "request_id": request_id,
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "error": {"code": code, "message": message},
                }
            )
        )

    @database_sync_to_async
    def _can_access_channel(self) -> bool:
        from apps.broadcast.models import BroadcastChannel, BroadcastSubscription
        from apps.organizations.models import OrganizationMember

        channel = BroadcastChannel.objects.filter(pk=self.channel_id, is_active=True).first()
        if not channel:
            return False

        is_org_member = OrganizationMember.objects.filter(
            organization=channel.organization,
            user=self.user,
            membership_status="active",
            is_deleted=False,
        ).exists()
        if not is_org_member:
            return False

        if channel.type == "private":
            return BroadcastSubscription.objects.filter(channel=channel, user=self.user, is_deleted=False).exists()
        return True

    @database_sync_to_async
    def _channel_context(self):
        from apps.broadcast.models import BroadcastChannel

        channel = BroadcastChannel.objects.filter(pk=self.channel_id).first()
        return {
            "interaction_id": str(channel.interaction_id) if channel and channel.interaction_id else None,
            "group_id": str(channel.group_id) if channel and channel.group_id else None,
        }

    @database_sync_to_async
    def _mark_delivered(self, delivery_id: str):
        from django.utils import timezone as dj_tz
        from apps.broadcast.models import BroadcastDelivery

        BroadcastDelivery.objects.filter(
            pk=delivery_id,
            user=self.user,
            message__channel_id=self.channel_id,
        ).exclude(status="seen").update(status="delivered", delivered_at=dj_tz.now())

    @database_sync_to_async
    def _mark_seen(self, delivery_id: str):
        from django.utils import timezone as dj_tz
        from apps.broadcast.models import BroadcastDelivery

        delivery = BroadcastDelivery.objects.filter(
            pk=delivery_id,
            user=self.user,
            message__channel_id=self.channel_id,
        ).first()
        if not delivery:
            return None

        delivery.status = "seen"
        delivery.read_at = dj_tz.now()
        delivery.save(update_fields=["status", "read_at", "updated_at_server"])
        return {
            "delivery_id": str(delivery.id),
            "message_id": str(delivery.message_id),
            "user_id": str(delivery.user_id),
            "status": delivery.status,
            "read_at": delivery.read_at.isoformat() if delivery.read_at else None,
        }
