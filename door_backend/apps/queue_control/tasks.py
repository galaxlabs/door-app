"""Background jobs for queue_control domain."""

from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@shared_task(name="queue_control.auto_end_sessions_for_closed_queues")
def auto_end_sessions_for_closed_queues() -> int:
    """End active sessions if their queue has been closed."""
    from .models import QueueSession

    return QueueSession.objects.filter(queue__status="closed", status="active").update(
        status="ended",
        ended_at=timezone.now(),
    )


@shared_task(name="queue_control.broadcast_queue_state")
def broadcast_queue_state(queue_id: str) -> bool:
    """Broadcast latest queue state snapshot to websocket room."""
    from .models import Queue, QueueTicket
    from .serializers import QueueSerializer

    try:
        queue = Queue.objects.get(pk=queue_id)
    except Queue.DoesNotExist:
        return False

    payload = {
        "queue": QueueSerializer(queue).data,
        "waiting_count": QueueTicket.objects.filter(queue=queue, status__in=["issued", "waiting"]).count(),
        "called_count": QueueTicket.objects.filter(queue=queue, status="called").count(),
        "current_serving": queue.current_serving,
    }

    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f"queue_{queue_id}",
        {"type": "ws_event", "event": "queue.state", "data": payload},
    )
    return True
