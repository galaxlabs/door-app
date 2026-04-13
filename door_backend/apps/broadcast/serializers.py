from rest_framework import serializers
from .models import (
    BroadcastChannel,
    BroadcastMessage,
    BroadcastSubscription,
    BroadcastDelivery,
    BroadcastRecipient,
)


class BroadcastChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastChannel
        fields = [
            "id", "organization", "group", "name", "description",
            "type", "is_active", "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class BroadcastMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastMessage
        fields = [
            "id", "channel", "sender", "title", "body", "type", "target_mode",
            "status", "payload", "scheduled_at", "sent_at",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "sender", "sent_at", "created_at_server", "updated_at_server"]


class BroadcastSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastSubscription
        fields = ["id", "channel", "user", "subscribed_at", "is_muted"]
        read_only_fields = ["id", "subscribed_at"]


class BroadcastRecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastRecipient
        fields = ["id", "message", "user"]
        read_only_fields = ["id"]


class BroadcastDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastDelivery
        fields = [
            "id", "message", "user", "device_id", "status",
            "delivered_at", "read_at", "failure_reason",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]
