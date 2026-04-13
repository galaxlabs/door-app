from django.db import transaction

from apps.chat.models import ChatMessage, MessageStatus


class ChatMessageService:
    @staticmethod
    @transaction.atomic
    def send_message(*, room, sender, msg_type: str, content: str = "", client_id: str = "", **extra):
        if client_id:
            existing = ChatMessage.objects.filter(sender=sender, client_id=client_id).first()
            if existing:
                return existing
        return ChatMessage.objects.create(
            room=room,
            sender=sender,
            type=msg_type,
            content=content,
            attachment=extra.get("attachment"),
            reply_to=extra.get("reply_to"),
            sender_device_id=extra.get("sender_device_id", ""),
            client_id=client_id,
            delivery_state="sent",
        )

    @staticmethod
    @transaction.atomic
    def update_status(*, message: ChatMessage, user, status: str, status_device_id: str = ""):
        status_obj, _ = MessageStatus.objects.update_or_create(
            message=message,
            user=user,
            defaults={"status": status, "status_device_id": status_device_id},
        )
        state_rank = {"queued": 0, "sent": 1, "delivered": 2, "seen": 3}
        if state_rank.get(status, 0) >= state_rank.get(message.delivery_state, 0):
            message.delivery_state = status
            message.save(update_fields=["delivery_state", "updated_at_server"])
        return status_obj
