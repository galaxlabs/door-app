from rest_framework import serializers
from .models import SyncQueue, ConflictLog, SyncCursor, DeviceOutbox


class SyncOperationSerializer(serializers.Serializer):
    entity_type = serializers.CharField()
    operation = serializers.ChoiceField(choices=["create", "update", "delete", "action"])
    client_id = serializers.CharField(required=False, allow_blank=True)
    idempotency_key = serializers.UUIDField(required=False, allow_null=True)
    entity_id = serializers.CharField(required=False, allow_blank=True)
    payload = serializers.JSONField(default=dict)
    created_at_client = serializers.DateTimeField(required=False, allow_null=True)
    updated_at_client = serializers.DateTimeField(required=False, allow_null=True)
    sequence = serializers.IntegerField()


class SyncUploadSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    last_sync_at = serializers.DateTimeField(required=False, allow_null=True)
    operations = SyncOperationSerializer(many=True)


class SyncPullSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    stream_name = serializers.CharField(required=False, default="core")
    since = serializers.CharField(required=False, allow_blank=True)
    entity_types = serializers.ListField(child=serializers.CharField())


class ConflictLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConflictLog
        fields = [
            "id", "entity_type", "entity_id", "server_version",
            "client_version", "resolution", "resolved_at", "created_at",
        ]


class SyncQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncQueue
        fields = [
            "id", "user", "device_id", "operation", "entity_type", "entity_id",
            "client_id", "idempotency_key", "payload", "status", "error_detail",
            "cursor_before", "cursor_after", "sequence", "synced_at",
            "created_at_client", "updated_at_client", "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class DeviceOutboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceOutbox
        fields = [
            "id", "user", "device_id", "entity_type", "entity_id", "operation",
            "payload", "event_version", "outbox_state", "retry_count",
            "next_retry_at", "acked_at", "created_at_server",
        ]
        read_only_fields = ["id", "created_at_server"]


class SyncCursorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncCursor
        fields = [
            "id", "user", "device_id", "stream_name", "last_sync_at",
            "last_seen_version", "cursor_token", "entity_types", "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]
