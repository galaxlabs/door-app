from rest_framework import serializers
from .models import ChatRoom, ChatRoomMember, ChatMessage, MessageStatus


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name", read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id", "room", "sender", "sender_name", "type",
            "content", "attachment", "reply_to", "sent_at",
            "edited_at", "is_deleted", "client_id", "sender_device_id",
            "delivery_state", "created_at_server", "updated_at_server",
        ]
        read_only_fields = [
            "id", "sender", "sender_name", "sent_at", "edited_at",
            "created_at_server", "updated_at_server",
        ]


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = [
            "id", "organization", "event", "group", "type", "name", "avatar",
            "status", "is_active", "created_by", "metadata",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class ChatRoomMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = ChatRoomMember
        fields = [
            "id", "room", "user", "user_name", "is_admin", "role",
            "joined_at", "left_at", "last_read_at",
        ]
        read_only_fields = ["id", "joined_at"]


class MessageStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageStatus
        fields = ["id", "message", "user", "status", "status_device_id", "updated_at"]
        read_only_fields = ["id", "updated_at"]
