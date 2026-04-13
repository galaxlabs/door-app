import secrets
from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from .models import QRCode, QRScan, ScanToken, QROwnerMember, QRAlert, QRAlertRecipient
from .services.owner_notification_service import QROwnerNotificationService


class QRCodeSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source="image", read_only=True)

    class Meta:
        model = QRCode
        fields = [
            "id", "organization", "event", "group", "queue",
            "label", "entity_type", "mode", "action_payload", "metadata",
            "payload_type", "payload_data",  # backward compatible fields
            "status", "scans_limit", "scans_count", "expires_at",
            "is_active", "image_url", "created_at_server", "updated_at_server",
        ]
        read_only_fields = [
            "id", "scans_count", "image_url", "created_at_server", "updated_at_server"
        ]


class QRScanSerializer(serializers.Serializer):
    qr_code_id = serializers.UUIDField()
    device_id = serializers.CharField(max_length=128, required=False, allow_blank=True)
    scan_source = serializers.ChoiceField(
        choices=QRScan.SCAN_SOURCE_CHOICES,
        required=False,
        default="camera",
    )
    raw_content = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False, default=dict)
    location_lat = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    location_lng = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

    def validate_qr_code_id(self, value):
        try:
            qr = QRCode.objects.get(pk=value, is_active=True)
        except QRCode.DoesNotExist:
            raise serializers.ValidationError("QR code not found or inactive.")
        if qr.is_expired:
            raise serializers.ValidationError("QR code has expired.")
        if qr.is_limit_reached:
            raise serializers.ValidationError("Scan limit reached for this QR code.")
        return value

    def create(self, validated_data):
        qr = QRCode.objects.select_for_update().get(pk=validated_data["qr_code_id"])
        scan = QRScan.objects.create(
            qr_code=qr,
            scanned_by=self.context["request"].user if self.context["request"].user.is_authenticated else None,
            device_id=validated_data.get("device_id", ""),
            scan_source=validated_data.get("scan_source", "camera"),
            raw_content=validated_data.get("raw_content", ""),
            metadata=validated_data.get("metadata", {}),
            location_lat=validated_data.get("location_lat"),
            location_lng=validated_data.get("location_lng"),
            entity_type=qr.entity_type,
            mode=qr.mode,
            action_payload=qr.action_payload or qr.payload_data,
        )
        QROwnerNotificationService.trigger_alert_for_scan(scan=scan)
        qr.scans_count += 1
        qr.save(update_fields=["scans_count"])

        token = ScanToken.objects.create(
            scan=scan,
            token=secrets.token_hex(32),
            expires_at=timezone.now() + timedelta(minutes=30),
        )
        return token


class ScanTokenSerializer(serializers.ModelSerializer):
    qr_label = serializers.CharField(source="scan.qr_code.label", read_only=True)
    entity_type = serializers.CharField(source="scan.entity_type", read_only=True)
    mode = serializers.CharField(source="scan.mode", read_only=True)
    action_payload = serializers.JSONField(source="scan.action_payload", read_only=True)
    alert_id = serializers.SerializerMethodField()

    def get_alert_id(self, obj):
        first_alert = obj.scan.alerts.order_by("-created_at_server").first()
        return str(first_alert.id) if first_alert else None

    class Meta:
        model = ScanToken
        fields = [
            "token", "status", "expires_at", "redeemed_at", "qr_label",
            "entity_type", "mode", "action_payload", "alert_id", "action_result", "failure_reason",
        ]


class QRScanLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRScan
        fields = [
            "id", "qr_code", "scanned_by", "device_id", "entity_type", "mode",
            "action_payload", "scan_source", "raw_content", "metadata",
            "location_lat", "location_lng", "scanned_at",
        ]
        read_only_fields = fields


class QROwnerMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = QROwnerMember
        fields = [
            "id",
            "qr_code",
            "owner",
            "member_user",
            "display_name",
            "phone",
            "email",
            "member_type",
            "notify_role",
            "priority",
            "availability",
            "can_respond",
            "is_active",
            "extra",
            "created_at_server",
            "updated_at_server",
        ]
        read_only_fields = ["id", "owner", "created_at_server", "updated_at_server"]


class QRAlertRecipientSerializer(serializers.ModelSerializer):
    member_display_name = serializers.CharField(source="member.display_name", read_only=True)

    class Meta:
        model = QRAlertRecipient
        fields = [
            "id",
            "member",
            "member_display_name",
            "notify_role",
            "delivery_status",
            "response_status",
            "notified_at",
            "responded_at",
            "response_note",
        ]
        read_only_fields = fields


class QRAlertSerializer(serializers.ModelSerializer):
    recipients = QRAlertRecipientSerializer(many=True, read_only=True)

    class Meta:
        model = QRAlert
        fields = [
            "id",
            "scan",
            "qr_code",
            "triggered_by",
            "status",
            "message",
            "responded_by_member",
            "responded_at",
            "cc_snapshot",
            "bcc_snapshot",
            "meta",
            "recipients",
            "created_at_server",
            "updated_at_server",
        ]
        read_only_fields = fields


class QRAlertRespondSerializer(serializers.Serializer):
    member_id = serializers.UUIDField()
    response_status = serializers.ChoiceField(choices=QRAlertRecipient.RESPONSE_STATUS_CHOICES)
    response_note = serializers.CharField(required=False, allow_blank=True)
