from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id", "user", "user_phone", "organization", "action",
            "entity_type", "entity_id", "payload", "before_json", "after_json",
            "context_json", "ip_address", "device_id", "user_agent", "request_id",
            "created_at", "created_at_server",
        ]
        read_only_fields = fields
