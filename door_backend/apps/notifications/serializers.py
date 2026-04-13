from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "user", "organization", "type", "title", "body", "data",
            "priority", "state", "is_read", "read_at", "archived_at", "expires_at",
            "source_entity_type", "source_entity_id",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]
