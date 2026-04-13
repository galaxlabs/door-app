from apps.chat.models import ChatRoom, ChatRoomMember
from apps.qr_engine.models import InteractionRecord


class ChatRoomService:
    @staticmethod
    def ensure_member(*, room: ChatRoom, user, role: str = "member") -> ChatRoomMember:
        member, _ = ChatRoomMember.objects.get_or_create(
            room=room,
            user=user,
            defaults={"role": role, "is_admin": role in {"admin", "moderator"}},
        )
        return member

    @classmethod
    def ensure_direct_room(cls, *, creator, other_user) -> ChatRoom:
        room = (
            ChatRoom.objects.filter(type="direct", is_deleted=False, members__user=creator)
            .filter(members__user=other_user)
            .distinct()
            .first()
        )
        if not room:
            room = ChatRoom.objects.create(
                type="direct",
                name="",
                created_by=creator,
                metadata={"direct_participants": sorted([str(creator.id), str(other_user.id)])},
            )
        cls.ensure_member(room=room, user=creator, role="admin")
        cls.ensure_member(room=room, user=other_user, role="member")
        return room

    @classmethod
    def ensure_interaction_room(cls, *, interaction: InteractionRecord, owner, members=None) -> ChatRoom:
        room = ChatRoom.objects.filter(interaction=interaction, is_deleted=False).first()
        if not room:
            room = ChatRoom.objects.create(
                organization=interaction.qr_entity.organization,
                event=interaction.qr_entity.event,
                group=interaction.qr_entity.group,
                interaction=interaction,
                type="interaction",
                name=interaction.template.name,
                created_by=owner,
                metadata={
                    "interaction_id": str(interaction.id),
                    "template_id": str(interaction.template_id),
                    "purpose": interaction.qr_entity.purpose,
                },
            )
        cls.ensure_member(room=room, user=owner, role="admin")
        if interaction.initiated_by_id:
            cls.ensure_member(room=room, user=interaction.initiated_by, role="member")
        for member in members or []:
            cls.ensure_member(room=room, user=member, role="member")
        return room
