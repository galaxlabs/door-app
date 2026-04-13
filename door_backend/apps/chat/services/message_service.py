from django.db import transaction

from apps.chat.models import ChatMessage


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
