import json
import uuid
from datetime import datetime, timezone

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket: ws://host/ws/chat/<room_id>/

        Incoming events:
            - message.send     { msg_type, content, client_id, reply_to, sender_device_id }
            - message.read     { message_id, status_device_id }
            - message.delivered{ message_id, status_device_id }
            - typing           { is_typing }
            - ping

        Outgoing events:
            - chat.connected
            - message.new
            - message.status
            - user.typing
            - ack
            - error
    """

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group_name = f"chat_{self.room_id}"
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        is_member = await self._is_member()
        if not is_member:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        room_context = await self._room_context()
        await self._send_event("chat.connected", {"room_id": self.room_id, **room_context})

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            await self._send_error("bad_json", "Invalid JSON payload.")
            return

        event_type = data.get("type")
        request_id = data.get("request_id") or str(uuid.uuid4())

        if event_type == "message.send":
            msg = await self._save_message(data)
            if msg:
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "ws_event", "event": "message.new", "data": msg},
                )
                await self._send_ack("message.send", request_id=request_id)
        elif event_type == "message.read":
            status_data = await self._mark_status(
                message_id=data.get("message_id"),
                status="seen",
                status_device_id=data.get("status_device_id", ""),
            )
            if status_data:
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "ws_event", "event": "message.status", "data": status_data},
                )
                await self._send_ack("message.read", request_id=request_id)
        elif event_type == "message.delivered":
            status_data = await self._mark_status(
                message_id=data.get("message_id"),
                status="delivered",
                status_device_id=data.get("status_device_id", ""),
            )
            if status_data:
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "ws_event", "event": "message.status", "data": status_data},
                )
                await self._send_ack("message.delivered", request_id=request_id)
        elif event_type == "typing":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "ws_event",
                    "event": "user.typing",
                    "data": {
                        "user_id": str(self.user.id),
                        "name": self.user.full_name,
                        "is_typing": data.get("is_typing", False),
                    },
                },
            )
        elif event_type == "ping":
            await self._send_event("pong", {"room_id": self.room_id}, request_id=request_id)
        else:
            await self._send_error("unknown_event", f"Unsupported event '{event_type}'.", request_id=request_id)

    async def ws_event(self, event):
        await self._send_event(event.get("event", "unknown"), event.get("data", {}), request_id=event.get("request_id"))

    async def message_new(self, event):
        await self._send_event("message.new", event.get("data", {}))

    async def message_status(self, event):
        await self._send_event("message.status", event.get("data", {}))

    async def user_typing(self, event):
        await self._send_event("user.typing", event.get("data", {}))

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
    def _is_member(self):
        from .models import ChatRoomMember
        return ChatRoomMember.objects.filter(room_id=self.room_id, user=self.user, is_deleted=False).exists()

    @database_sync_to_async
    def _room_context(self):
        from .models import ChatRoom

        room = ChatRoom.objects.filter(pk=self.room_id).first()
        return {
            "interaction_id": str(room.interaction_id) if room and room.interaction_id else None,
            "room_type": room.type if room else None,
        }

    @database_sync_to_async
    def _save_message(self, data):
        from .models import ChatMessage
        from .serializers import ChatMessageSerializer
        # Idempotency: skip if client_id already exists
        client_id = data.get("client_id", "")
        if client_id:
            existing = ChatMessage.objects.filter(sender=self.user, client_id=client_id).first()
            if existing:
                return ChatMessageSerializer(existing).data
        msg = ChatMessage.objects.create(
            room_id=self.room_id,
            sender=self.user,
            type=data.get("msg_type", "text"),
            content=data.get("content", ""),
            sender_device_id=data.get("sender_device_id", ""),
            reply_to_id=data.get("reply_to"),
            delivery_state="sent",
            client_id=client_id,
        )
        return ChatMessageSerializer(msg).data

    @database_sync_to_async
    def _mark_status(self, message_id, status: str, status_device_id: str = ""):
        from .models import MessageStatus
        if not message_id:
            return None

        obj, _ = MessageStatus.objects.update_or_create(
            message_id=message_id,
            user=self.user,
            defaults={"status": status, "status_device_id": status_device_id},
        )
        return {
            "message_id": str(message_id),
            "user_id": str(self.user.id),
            "status": obj.status,
            "status_device_id": obj.status_device_id,
            "updated_at": obj.updated_at.isoformat(),
        }
