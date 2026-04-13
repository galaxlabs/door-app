"""Background jobs for chat domain."""

from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@shared_task(name="chat.notify_message_status")
def notify_message_status(message_id: str, user_id: str, status: str) -> bool:
    """Publish chat message status updates to websocket room."""
    from .models import ChatMessage

    try:
        message = ChatMessage.objects.select_related("room").get(pk=message_id)
    except ChatMessage.DoesNotExist:
        return False

    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f"chat_{message.room_id}",
        {
            "type": "ws_event",
            "event": "message.status",
            "data": {
                "message_id": str(message.id),
                "user_id": user_id,
                "status": status,
            },
        },
    )
    return True
