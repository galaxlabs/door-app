import secrets
from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from .models import (
    InteractionTemplate,
    TemplateField,
    TemplateWorkflowState,
    TemplateAction,
    NotificationRule,
    InteractionRecord,
    InteractionAuditLog,
    QRCode,
    QRScan,
    ScanToken,
    QROwnerMember,
    QRAlert,
    QRAlertRecipient,
)
from .services.owner_notification_service import QROwnerNotificationService
from .services.interaction_service import InteractionRuntimeService
from .services.template_service import QRTemplateService


class InteractionTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionTemplate
        fields = [
            "id",
            "name",
            "category",
            "description",
            "icon",
            "default_language",
            "is_public",
            "supports_offline",
            "version",
            "schema_json",
            "created_at_server",
            "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class TemplateFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateField
        fields = [
            "id",
            "template",
            "field_key",
            "label",
            "field_type",
            "is_required",
            "default_value",
            "options_json",
            "validation_json",
            "visibility_rule_json",
            "created_at_server",
            "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class TemplateWorkflowStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateWorkflowState
        fields = [
            "id",
            "template",
            "state_name",
            "state_type",
            "order",
            "color",
            "is_initial",
            "is_final",
            "created_at_server",
            "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class TemplateActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateAction
        fields = [
            "id",
            "template",
            "action_name",
            "action_key",
            "source_state",
            "target_state",
            "role_required",
            "button_style",
            "action_config_json",
            "created_at_server",
            "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class NotificationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationRule
        fields = [
            "id",
            "template",
            "trigger_event",
            "audience_type",
            "audience_config",
            "channel",
            "priority",
            "fallback_rule_json",
            "created_at_server",
            "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class TemplateWorkflowStateSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateWorkflowState
        fields = ["id", "state_name", "state_type", "order", "color", "is_initial", "is_final"]
        read_only_fields = fields


class InteractionAuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.full_name", read_only=True)
    from_state = TemplateWorkflowStateSummarySerializer(read_only=True)
    to_state = TemplateWorkflowStateSummarySerializer(read_only=True)

    class Meta:
        model = InteractionAuditLog
        fields = [
            "id",
            "interaction",
            "actor",
            "actor_name",
            "action",
            "from_state",
            "to_state",
            "snapshot_json",
            "device_id",
            "created_at_client",
            "created_at_server",
        ]
        read_only_fields = fields


class InteractionRecordSerializer(serializers.ModelSerializer):
    current_state = TemplateWorkflowStateSummarySerializer(read_only=True)
    initiated_by_name = serializers.CharField(source="initiated_by.full_name", read_only=True)

    class Meta:
        model = InteractionRecord
        fields = [
            "id",
            "template",
            "qr_entity",
            "scan",
            "initiated_by",
            "initiated_by_name",
            "initiated_at",
            "current_state",
            "payload_json",
            "status",
            "sync_status",
            "version",
            "created_at_server",
            "updated_at_server",
        ]
        read_only_fields = fields


class InteractionActionSerializer(serializers.Serializer):
    action_key = serializers.CharField(max_length=100)
    device_id = serializers.CharField(max_length=128, required=False, allow_blank=True)
    payload_json = serializers.JSONField(required=False, default=dict)


class TemplatePackSeedSerializer(serializers.Serializer):
    pack_keys = serializers.ListField(child=serializers.CharField(), allow_empty=False)


class TemplatePackAdminSetupSerializer(serializers.Serializer):
    pack_key = serializers.CharField(max_length=100)
    organization = serializers.UUIDField(required=False, allow_null=True)
    event = serializers.UUIDField(required=False, allow_null=True)
    group = serializers.UUIDField(required=False, allow_null=True)
    queue = serializers.UUIDField(required=False, allow_null=True)
    name = serializers.CharField(max_length=255)
    owner_type = serializers.CharField(max_length=50, required=False, allow_blank=True)
    owner_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    metadata_json = serializers.JSONField(required=False, default=dict)


class QRCodeRuntimeActionSerializer(serializers.Serializer):
    operation = serializers.CharField(max_length=100)
    device_id = serializers.CharField(max_length=128, required=False, allow_blank=True)


class QRCodeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="label")
    entity_type = serializers.ChoiceField(choices=QRCode.ENTITY_TYPE_CHOICES, required=False)
    mode = serializers.ChoiceField(choices=QRCode.MODE_CHOICES, required=False)
    template = serializers.PrimaryKeyRelatedField(
        queryset=InteractionTemplate.objects.all(),
        required=False,
        allow_null=True,
    )
    expiry = serializers.DateTimeField(source="expires_at", required=False, allow_null=True)
    metadata_json = serializers.JSONField(required=False)
    image_url = serializers.ImageField(source="image", read_only=True)

    class Meta:
        model = QRCode
        fields = [
            "id", "organization", "event", "group", "queue",
            "name", "label", "owner_type", "owner_id", "template", "purpose",
            "entity_type", "mode", "action_payload", "metadata", "metadata_json",
            "payload_type", "payload_data",  # backward compatible fields
            "status", "qr_token", "scans_limit", "scans_count", "expiry", "expires_at",
            "is_active", "image_url", "created_at_server", "updated_at_server",
        ]
        read_only_fields = [
            "id", "label", "qr_token", "scans_count", "image_url", "created_at_server", "updated_at_server"
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        template = attrs.get("template") or getattr(self.instance, "template", None)
        owner_type = attrs.get("owner_type") or getattr(self.instance, "owner_type", "")
        if template:
            QRTemplateService.validate_template_configuration(template=template)
            attrs.setdefault("entity_type", owner_type or "organization")
            attrs.setdefault("mode", "custom_action")
            attrs.setdefault("payload_type", "custom_action")
            attrs.setdefault("purpose", template.category)
        return attrs

    def create(self, validated_data):
        label = validated_data.pop("label")
        metadata_json = validated_data.get("metadata_json")
        if metadata_json and not validated_data.get("metadata"):
            validated_data["metadata"] = metadata_json
        return QRTemplateService.create_qr_code(label=label, **validated_data)

    def update(self, instance, validated_data):
        label = validated_data.pop("label", None)
        metadata_json = validated_data.get("metadata_json")
        if label is not None:
            instance.label = label
        if metadata_json is not None:
            instance.metadata_json = metadata_json
            if not validated_data.get("metadata"):
                instance.metadata = metadata_json
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


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
        interaction = InteractionRuntimeService.create_from_scan(scan=scan)
        QROwnerNotificationService.trigger_alert_for_scan(scan=scan)
        qr.scans_count += 1
        qr.save(update_fields=["scans_count"])

        token = ScanToken.objects.create(
            scan=scan,
            token=secrets.token_hex(32),
            expires_at=timezone.now() + timedelta(minutes=30),
        )
        token.action_result = {
            "interaction_id": str(interaction.id) if interaction else None,
            "interaction_status": interaction.status if interaction else "",
        }
        token.save(update_fields=["action_result"])
        return token


class ScanTokenSerializer(serializers.ModelSerializer):
    qr_label = serializers.CharField(source="scan.qr_code.label", read_only=True)
    entity_type = serializers.CharField(source="scan.entity_type", read_only=True)
    mode = serializers.CharField(source="scan.mode", read_only=True)
    action_payload = serializers.JSONField(source="scan.action_payload", read_only=True)
    template = serializers.JSONField(source="scan.template_snapshot", read_only=True)
    purpose = serializers.CharField(source="scan.qr_code.purpose", read_only=True)
    alert_id = serializers.SerializerMethodField()
    interaction_id = serializers.SerializerMethodField()
    interaction_status = serializers.SerializerMethodField()
    interaction_state = serializers.SerializerMethodField()

    def get_alert_id(self, obj):
        first_alert = obj.scan.alerts.order_by("-created_at_server").first()
        return str(first_alert.id) if first_alert else None

    def get_interaction_id(self, obj):
        interaction = getattr(obj.scan, "interaction_record", None)
        return str(interaction.id) if interaction else None

    def get_interaction_status(self, obj):
        interaction = getattr(obj.scan, "interaction_record", None)
        return interaction.status if interaction else None

    def get_interaction_state(self, obj):
        interaction = getattr(obj.scan, "interaction_record", None)
        if not interaction or not interaction.current_state_id:
            return None
        return TemplateWorkflowStateSummarySerializer(interaction.current_state).data

    class Meta:
        model = ScanToken
        fields = [
            "token", "status", "expires_at", "redeemed_at", "qr_label",
            "entity_type", "mode", "purpose", "template", "action_payload",
            "interaction_id", "interaction_status", "interaction_state",
            "alert_id", "action_result", "failure_reason",
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
