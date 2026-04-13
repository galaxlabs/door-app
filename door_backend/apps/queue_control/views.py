from django.utils import timezone
from rest_framework import viewsets, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.db import transaction

from .models import Queue, QueueTicket, QueueSession
from .serializers import QueueSerializer, QueueTicketSerializer


def _broadcast_queue(queue_id):
    from .models import Queue
    from .serializers import QueueSerializer
    layer = get_channel_layer()
    q = Queue.objects.get(pk=queue_id)
    async_to_sync(layer.group_send)(
        f"queue_{queue_id}",
        {"type": "queue.state", "data": QueueSerializer(q).data},
    )


class QueueViewSet(viewsets.ModelViewSet):
    serializer_class = QueueSerializer
    filterset_fields = ["organization", "event", "status"]

    def get_queryset(self):
        return Queue.objects.filter(
            organization__members__user=self.request.user
        ).distinct()

    @action(detail=True, methods=["post"], url_path="join")
    def join(self, request, pk=None):
        queue = self.get_object()
        if queue.status != "open":
            return Response({"detail": "Queue is not open."}, status=status.HTTP_400_BAD_REQUEST)

        device_id = request.data.get("device_id", "")

        with transaction.atomic():
            locked_queue = Queue.objects.select_for_update().get(pk=queue.pk)
            session = (
                locked_queue.sessions.filter(status="active")
                .order_by("-started_at")
                .first()
            )
            if session is None:
                session = QueueSession.objects.create(
                    queue=locked_queue,
                    started_by=request.user if request.user.is_authenticated else None,
                    status="active",
                )

            last_ticket = (
                locked_queue.tickets.filter(session=session)
                .order_by("-number")
                .first()
            )
            ticket_number = (last_ticket.number + 1) if last_ticket else 1

            ticket = QueueTicket.objects.create(
                queue=locked_queue,
                session=session,
                user=request.user if request.user.is_authenticated else None,
                device_id=device_id,
                number=ticket_number,
                status="issued",
            )

        _broadcast_queue(queue.id)
        return Response(
            {
                "ticket_id": str(ticket.id),
                "ticket_number": ticket.number,
                "status": ticket.status,
                "queue_id": str(queue.id),
            }
        )

    @action(detail=True, methods=["post"], url_path="call-next")
    def call_next(self, request, pk=None):
        """Call the next waiting ticket."""
        queue = self.get_object()
        ticket = queue.tickets.filter(status="waiting").order_by("number").first()
        if not ticket:
            return Response({"detail": "No waiting tickets."}, status=status.HTTP_400_BAD_REQUEST)

        ticket.status = "called"
        ticket.called_at = timezone.now()
        ticket.desk_number = request.data.get("desk_number")
        ticket.save(update_fields=["status", "called_at", "desk_number"])
        queue.current_serving = ticket.number
        queue.save(update_fields=["current_serving"])

        layer = get_channel_layer()
        async_to_sync(layer.group_send)(
            f"queue_{queue.id}",
            {"type": "ticket.called", "data": QueueTicketSerializer(ticket).data},
        )
        _broadcast_queue(queue.id)
        return Response(QueueTicketSerializer(ticket).data)

    @action(detail=True, methods=["post"], url_path="toggle")
    def toggle_status(self, request, pk=None):
        queue = self.get_object()
        new_status = request.data.get("status")
        if new_status not in ("open", "paused", "closed"):
            return Response({"detail": "Invalid status."}, status=400)
        queue.status = new_status
        queue.save(update_fields=["status"])
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(
            f"queue_{queue.id}",
            {"type": "queue.status", "data": {"status": new_status}},
        )
        return Response({"ok": True, "status": new_status})


class QueueTicketViewSet(viewsets.ModelViewSet):
    serializer_class = QueueTicketSerializer
    filterset_fields = ["status"]

    def get_queryset(self):
        return QueueTicket.objects.filter(queue_id=self.kwargs["queue_pk"])

    @action(detail=True, methods=["post"])
    def serve(self, request, queue_pk=None, pk=None):
        ticket = self.get_object()
        ticket.status = "serving"
        ticket.served_at = timezone.now()
        ticket.save(update_fields=["status", "served_at"])
        _broadcast_queue(queue_pk)
        return Response(QueueTicketSerializer(ticket).data)

    @action(detail=True, methods=["post"])
    def done(self, request, queue_pk=None, pk=None):
        ticket = self.get_object()
        ticket.status = "done"
        ticket.save(update_fields=["status"])
        _broadcast_queue(queue_pk)
        return Response(QueueTicketSerializer(ticket).data)
