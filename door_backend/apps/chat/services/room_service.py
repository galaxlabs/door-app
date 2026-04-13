from apps.chat.models import ChatRoom, ChatRoomMember


class ChatRoomService:
    @staticmethod
    def ensure_member(*, room: ChatRoom, user, role: str = "member") -> ChatRoomMember:
        member, _ = ChatRoomMember.objects.get_or_create(
            room=room,
            user=user,
            defaults={"role": role, "is_admin": role in {"admin", "moderator"}},
        )
        return member
