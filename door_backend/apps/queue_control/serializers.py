from rest_framework import serializers
from .models import Queue, QueueSession, QueueTicket, QueueActionLog


class QueueTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueueTicket
        fields = [
            "id", "queue", "session", "issued_from_scan_token",
            "user", "device_id", "number", "status", "priority", "desk_number",
            "issued_at", "called_at", "recalled_at", "completed_at", "cancelled_at",
            "served_at", "estimated_wait_snapshot", "notes", "metadata",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "number", "created_at_server", "updated_at_server"]


class QueueSerializer(serializers.ModelSerializer):
    waiting_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Queue
        fields = [
            "id", "organization", "event", "group", "name", "description",
            "queue_type", "max_capacity", "current_serving", "status",
            "is_token_based", "estimated_wait_minutes", "waiting_count",
            "allow_rejoin", "metadata", "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "current_serving", "waiting_count", "created_at_server", "updated_at_server"]


class QueueSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueueSession
        fields = [
            "id", "queue", "started_by", "ended_by", "status",
            "started_at", "ended_at", "current_token_number",
            "last_called_token_number", "metadata",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class QueueActionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueueActionLog
        fields = [
            "id", "queue", "session", "ticket", "actor_user", "actor_device_id",
            "action", "before_state", "after_state", "meta", "created_at_server",
        ]
        read_only_fields = fields
