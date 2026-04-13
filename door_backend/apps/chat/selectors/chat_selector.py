from apps.chat.models import ChatMessage, ChatRoom


class ChatSelector:
    @staticmethod
    def user_rooms(user):
        return ChatRoom.objects.filter(members__user=user, is_active=True).distinct()

    @staticmethod
    def room_messages(room_id):
        return ChatMessage.objects.filter(room_id=room_id, is_deleted=False).select_related("sender")
