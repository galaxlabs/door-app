import json
import uuid
from datetime import datetime, timezone

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class QueueConsumer(AsyncWebsocketConsumer):
    """
        Phase-1 Queue WebSocket contract.

        URL:
            ws://host/ws/queues/<queue_id>/?token=<jwt>

        Client -> Server events:
            - queue.state.request
            - queue.join                { device_id }
            - ticket.cancel             { ticket_id? }
            - ping

        Server -> Client events:
            - queue.state               { queue, waiting_count, called_count, current_serving }
            - ticket.issued             { ticket }
            - ticket.updated            { ticket }
            - ticket.called             { ticket }
            - queue.status              { status }
            - ack                       { request_id, action }
            - error                     { code, message }

        Backward-compat support:
            Incoming aliases: join, cancel
            Group handler aliases: queue_state, ticket_called, ticket_update, queue_status
    """

    async def connect(self):
        self.queue_id = self.scope["url_route"]["kwargs"]["queue_id"]
        self.group_name = f"queue_{self.queue_id}"
        self.user = self.scope.get("user")

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self._send_event("queue.connected", {"queue_id": self.queue_id})
        await self._push_state()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            await self._send_error("bad_json", "Invalid JSON payload.")
            return

        event_type = (data.get("type") or "").strip()
        request_id = data.get("request_id") or str(uuid.uuid4())

        if event_type in {"queue.state.request"}:
            await self._push_state(request_id=request_id)
            return

        # Backward-compat aliases
        if event_type in {"queue.join", "join"}:
            ticket = await self._handle_join(data)
            if not ticket:
                await self._send_error("queue_join_failed", "Unable to join queue.", request_id=request_id)
                return
            await self._send_ack("queue.join", request_id=request_id)
            await self._group_emit("ticket.issued", ticket)
            await self._push_state()
            return

        if event_type in {"ticket.cancel", "cancel"}:
            updated_ticket = await self._handle_cancel(data)
            if not updated_ticket:
                await self._send_error("ticket_not_found", "No cancellable ticket found.", request_id=request_id)
                return
            await self._send_ack("ticket.cancel", request_id=request_id)
            await self._group_emit("ticket.updated", updated_ticket)
            await self._push_state()
            return

        if event_type == "ping":
            await self._send_event("pong", {"queue_id": self.queue_id}, request_id=request_id)
            return

        await self._send_error("unknown_event", f"Unsupported event '{event_type}'.", request_id=request_id)

    async def ws_event(self, event):
        await self._send_event(event.get("event", "unknown"), event.get("data", {}), request_id=event.get("request_id"))

    # ---- Group message handlers ----
    async def queue_state(self, event):
        await self._send_event("queue.state", event.get("data", {}))

    async def ticket_called(self, event):
        await self._send_event("ticket.called", event.get("data", {}))

    async def ticket_update(self, event):
        await self._send_event("ticket.updated", event.get("data", {}))

    async def queue_status(self, event):
        await self._send_event("queue.status", event.get("data", {}))

    async def _send_event(self, event: str, data: dict, request_id: str | None = None):
        payload = {
            "event": event,
            "ok": True,
            "request_id": request_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        await self.send(json.dumps(payload))

    async def _send_ack(self, action: str, request_id: str | None = None):
        await self._send_event("ack", {"action": action}, request_id=request_id)

    async def _send_error(self, code: str, message: str, request_id: str | None = None):
        payload = {
            "event": "error",
            "ok": False,
            "request_id": request_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "error": {"code": code, "message": message},
        }
        await self.send(json.dumps(payload))

    async def _group_emit(self, event_name: str, data: dict):
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "ws_event",
                "event": event_name,
                "data": data,
            },
        )

    async def _push_state(self, request_id: str | None = None):
        state = await self._get_queue_state()
        await self._send_event("queue.state", state, request_id=request_id)

    # ---- DB helpers ----
    @database_sync_to_async
    def _get_queue_state(self):
        from .models import Queue, QueueTicket
        from .serializers import QueueSerializer

        try:
            q = Queue.objects.get(pk=self.queue_id)
            return {
                "queue": QueueSerializer(q).data,
                "waiting_count": QueueTicket.objects.filter(queue=q, status__in=["issued", "waiting"]).count(),
                "called_count": QueueTicket.objects.filter(queue=q, status="called").count(),
                "current_serving": q.current_serving,
            }
        except Queue.DoesNotExist:
            return {}

    @database_sync_to_async
    def _handle_join(self, data):
        from .models import Queue, QueueSession, QueueTicket
        from .serializers import QueueTicketSerializer
        from django.db import transaction

        with transaction.atomic():
            q = Queue.objects.select_for_update().get(pk=self.queue_id)
            if q.status != "open":
                return None

            session = q.sessions.filter(status="active").order_by("-started_at").first()
            if not session:
                session = QueueSession.objects.create(queue=q, status="active")

            last = q.tickets.filter(session=session).order_by("-number").first()
            number = (last.number + 1) if last else 1

            ticket = QueueTicket.objects.create(
                queue=q,
                session=session,
                user=self.user if self.user and self.user.is_authenticated else None,
                number=number,
                device_id=data.get("device_id", ""),
                status="issued",
            )

        return QueueTicketSerializer(ticket).data

    @database_sync_to_async
    def _handle_cancel(self, data):
        from .models import QueueTicket
        from .serializers import QueueTicketSerializer

        qs = QueueTicket.objects.filter(queue_id=self.queue_id, status__in=["issued", "waiting", "called", "recalled"])
        ticket_id = data.get("ticket_id")

        if ticket_id:
            qs = qs.filter(pk=ticket_id)
        elif self.user and self.user.is_authenticated:
            qs = qs.filter(user=self.user)
        else:
            qs = qs.filter(device_id=data.get("device_id", ""))

        ticket = qs.order_by("-issued_at", "-number").first()
        if not ticket:
            return None

        ticket.status = "cancelled"
        ticket.save(update_fields=["status", "updated_at_server"])
        return QueueTicketSerializer(ticket).data
