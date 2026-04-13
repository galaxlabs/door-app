import uuid
import qrcode
import io
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

from common.models import SoftDeleteModel


class QRCode(SoftDeleteModel):
    ENTITY_TYPE_CHOICES = [
        ("organization", "Organization"),
        ("event", "Event"),
        ("group", "Group"),
        ("queue", "Queue"),
    ]
    MODE_CHOICES = [
        ("check_in", "Check-In"),
        ("queue_join", "Queue Join"),
        ("open_chat", "Open Chat"),
        ("subscribe_broadcast", "Subscribe Broadcast"),
        ("custom_action", "Custom Action"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("archived", "Archived"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qr_codes",
    )
    event = models.ForeignKey(
        "organizations.Event",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qr_codes",
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qr_codes",
    )
    queue = models.ForeignKey(
        "queue_control.Queue",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qr_codes",
    )

    label = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES, db_index=True)
    mode = models.CharField(max_length=30, choices=MODE_CHOICES, db_index=True)
    action_payload = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Backward-compatible payload fields (to be deprecated after serializers migration)
    payload_type = models.CharField(max_length=30, choices=MODE_CHOICES, default="custom_action")
    payload_data = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="active", db_index=True)
    scans_limit = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    scans_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    image = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )

    class Meta:
        db_table = "qr_codes"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["event"]),
            models.Index(fields=["group"]),
            models.Index(fields=["queue"]),
            models.Index(fields=["entity_type", "mode", "is_active"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["updated_at_server"]),
        ]
        constraints = [
            models.CheckConstraint(check=Q(scans_limit__gte=0), name="qr_scans_limit_gte_0"),
            models.CheckConstraint(check=Q(scans_count__gte=0), name="qr_scans_count_gte_0"),
        ]

    def save(self, *args, **kwargs):
        # Keep backward compatibility in payload fields during migration period.
        if self.mode and not self.payload_type:
            self.payload_type = self.mode
        if self.action_payload and not self.payload_data:
            self.payload_data = self.action_payload

        if not self.image:
            self._generate_image()
        super().save(*args, **kwargs)

    def _generate_image(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(str(self.id))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        self.image.save(f"{self.id}.png", ContentFile(buffer.getvalue()), save=False)

    def __str__(self):
        return f"QR:{self.label} [{self.organization}]"

    @property
    def is_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

    @property
    def is_limit_reached(self):
        return self.scans_limit > 0 and self.scans_count >= self.scans_limit


class QRScan(SoftDeleteModel):
    SCAN_SOURCE_CHOICES = [
        ("camera", "Camera"),
        ("imported", "Imported"),
        ("nfc_bridge", "NFC Bridge"),
    ]

    qr_code = models.ForeignKey(QRCode, on_delete=models.CASCADE, related_name="scans")
    scanned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qr_scans",
    )
    device_id = models.CharField(max_length=128, blank=True, db_index=True)
    entity_type = models.CharField(max_length=20, choices=QRCode.ENTITY_TYPE_CHOICES, db_index=True)
    mode = models.CharField(max_length=30, choices=QRCode.MODE_CHOICES, db_index=True)
    action_payload = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    scan_source = models.CharField(max_length=20, choices=SCAN_SOURCE_CHOICES, default="camera")
    raw_content = models.TextField(blank=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "qr_scans"
        indexes = [
            models.Index(fields=["qr_code", "scanned_at"]),
            models.Index(fields=["scanned_by", "scanned_at"]),
            models.Index(fields=["device_id", "scanned_at"]),
            models.Index(fields=["entity_type", "mode"]),
            models.Index(fields=["updated_at_server"]),
        ]

    def save(self, *args, **kwargs):
        if not self.entity_type:
            self.entity_type = self.qr_code.entity_type
        if not self.mode:
            self.mode = self.qr_code.mode
        if not self.action_payload:
            self.action_payload = self.qr_code.action_payload or self.qr_code.payload_data
        super().save(*args, **kwargs)


class ScanToken(SoftDeleteModel):
    STATUS_CHOICES = [
        ("issued", "Issued"),
        ("redeemed", "Redeemed"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    scan = models.OneToOneField(QRScan, on_delete=models.CASCADE, related_name="token_obj")
    token = models.CharField(max_length=96, unique=True, db_index=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="issued", db_index=True)
    expires_at = models.DateTimeField()
    redeemed_at = models.DateTimeField(null=True, blank=True)
    redeemed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="redeemed_scan_tokens",
    )
    queue_ticket = models.ForeignKey(
        "queue_control.QueueTicket",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scan_tokens",
    )
    action_result = models.JSONField(default=dict, blank=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        db_table = "qr_scan_tokens"
        indexes = [
            models.Index(fields=["status", "expires_at"]),
            models.Index(fields=["scan"]),
            models.Index(fields=["updated_at_server"]),
        ]

    def __str__(self):
        return f"ScanToken({self.status})"


class QROwnerMember(SoftDeleteModel):
    MEMBER_TYPE_CHOICES = [
        ("family", "Family"),
        ("team", "Team"),
        ("office", "Office"),
    ]
    NOTIFY_ROLE_CHOICES = [
        ("to", "TO"),
        ("cc", "CC"),
        ("bcc", "BCC"),
    ]
    AVAILABILITY_CHOICES = [
        ("available", "Available"),
        ("unavailable", "Unavailable"),
        ("away", "Away"),
    ]

    qr_code = models.ForeignKey(
        QRCode,
        on_delete=models.CASCADE,
        related_name="owner_members",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_qr_members",
    )
    member_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qr_owner_memberships",
    )
    display_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    member_type = models.CharField(max_length=16, choices=MEMBER_TYPE_CHOICES, default="team", db_index=True)
    notify_role = models.CharField(max_length=8, choices=NOTIFY_ROLE_CHOICES, default="to", db_index=True)
    priority = models.PositiveSmallIntegerField(default=1)
    availability = models.CharField(max_length=16, choices=AVAILABILITY_CHOICES, default="available", db_index=True)
    can_respond = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, db_index=True)
    extra = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "qr_owner_members"
        indexes = [
            models.Index(fields=["qr_code", "is_active", "priority"]),
            models.Index(fields=["owner", "member_type"]),
            models.Index(fields=["notify_role", "availability"]),
            models.Index(fields=["updated_at_server"]),
        ]

    def __str__(self):
        return f"{self.display_name} ({self.notify_role})"


class QRAlert(SoftDeleteModel):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("responded", "Responded"),
        ("closed", "Closed"),
    ]

    scan = models.ForeignKey(QRScan, on_delete=models.CASCADE, related_name="alerts")
    qr_code = models.ForeignKey(QRCode, on_delete=models.CASCADE, related_name="alerts")
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_qr_alerts",
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="open", db_index=True)
    message = models.TextField(blank=True)
    responded_by_member = models.ForeignKey(
        QROwnerMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_alerts",
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    cc_snapshot = models.JSONField(default=list, blank=True)
    bcc_snapshot = models.JSONField(default=list, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "qr_alerts"
        indexes = [
            models.Index(fields=["qr_code", "status", "created_at_server"]),
            models.Index(fields=["scan"]),
            models.Index(fields=["updated_at_server"]),
        ]

    def __str__(self):
        return f"QRAlert({self.qr_code_id}, {self.status})"


class QRAlertRecipient(SoftDeleteModel):
    DELIVERY_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]
    RESPONSE_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("unavailable", "Unavailable"),
        ("declined", "Declined"),
        ("no_response", "No Response"),
    ]

    alert = models.ForeignKey(QRAlert, on_delete=models.CASCADE, related_name="recipients")
    member = models.ForeignKey(QROwnerMember, on_delete=models.CASCADE, related_name="alert_deliveries")
    notify_role = models.CharField(max_length=8, choices=QROwnerMember.NOTIFY_ROLE_CHOICES, default="to", db_index=True)
    delivery_status = models.CharField(max_length=16, choices=DELIVERY_STATUS_CHOICES, default="pending", db_index=True)
    response_status = models.CharField(max_length=16, choices=RESPONSE_STATUS_CHOICES, default="pending", db_index=True)
    notified_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    response_note = models.TextField(blank=True)

    class Meta:
        db_table = "qr_alert_recipients"
        unique_together = [("alert", "member")]
        indexes = [
            models.Index(fields=["alert", "notify_role"]),
            models.Index(fields=["member", "response_status"]),
            models.Index(fields=["updated_at_server"]),
        ]

    def __str__(self):
        return f"QRAlertRecipient({self.alert_id}, {self.member_id})"
