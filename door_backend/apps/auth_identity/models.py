import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

from common.models import UUIDModel, SyncableModel


def _generate_public_id() -> str:
    return f"u_{uuid.uuid4().hex[:20]}"


def _generate_anonymous_id() -> str:
    return f"anon_{uuid.uuid4().hex[:24]}"


# ---------------------------------------------------------------------------
# User Manager
# ---------------------------------------------------------------------------
class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra):
        if not phone:
            raise ValueError("Phone number is required")
        user = self.model(phone=phone, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(phone, password, **extra)


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("super_admin", "Super Admin"),
        ("owner", "Owner"),
        ("organization_admin", "Organization Admin"),
        ("manager", "Manager"),
        ("group_leader", "Group Leader"),
        ("staff", "Staff"),
        ("general_user", "General User"),
    ]
    LOCALE_CHOICES = [("en", "English"), ("ar", "Arabic"), ("ur", "Urdu")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    public_id = models.CharField(max_length=32, unique=True, default=_generate_public_id)
    anonymous_id = models.CharField(max_length=40, unique=True, default=_generate_anonymous_id)

    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    full_name = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    timezone = models.CharField(max_length=64, default="UTC")
    role = models.CharField(max_length=24, choices=ROLE_CHOICES, default="general_user")
    locale = models.CharField(max_length=5, choices=LOCALE_CHOICES, default="en")

    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_seen_at = models.DateTimeField(null=True, blank=True)

    default_organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="default_users",
    )

    # Sync fields (User is syncable for profile updates across devices)
    created_at_client = models.DateTimeField(null=True, blank=True)
    updated_at_client = models.DateTimeField(null=True, blank=True)
    created_at_server = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at_server = models.DateTimeField(auto_now=True, db_index=True)
    sync_status = models.CharField(
        max_length=24,
        choices=SyncableModel.SyncStatus.choices,
        default=SyncableModel.SyncStatus.SYNCED,
        db_index=True,
    )
    version = models.BigIntegerField(default=1)
    created_by_device_id = models.CharField(max_length=128, blank=True)
    last_modified_by_device_id = models.CharField(max_length=128, blank=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "auth_users"
        indexes = [
            models.Index(fields=["phone"]),
            models.Index(fields=["public_id"]),
            models.Index(fields=["anonymous_id"]),
            models.Index(fields=["role", "is_active"]),
            models.Index(fields=["updated_at_server"]),
        ]

    def __str__(self):
        return f"{self.full_name or self.phone}"

    @property
    def is_verified(self):
        """Backward-compatible alias for older code paths."""
        return self.is_phone_verified

    def mark_seen(self):
        self.last_seen_at = timezone.now()
        self.save(update_fields=["last_seen_at"])


# ---------------------------------------------------------------------------
# OTP
# ---------------------------------------------------------------------------
class OTP(models.Model):
    class Channel(models.TextChoices):
        SMS = "sms", "SMS"
        WHATSAPP = "whatsapp", "WhatsApp"
        EMAIL = "email", "Email"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, db_index=True)
    code = models.CharField(max_length=8)
    channel = models.CharField(max_length=12, choices=Channel.choices, default=Channel.SMS)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    attempt_count = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=5)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False, db_index=True)
    consumed_at = models.DateTimeField(null=True, blank=True)
    request_ip = models.GenericIPAddressField(null=True, blank=True)
    request_user_agent = models.TextField(blank=True)
    created_at_server = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_otps"
        indexes = [
            models.Index(fields=["phone", "used"]),
            models.Index(fields=["phone", "status", "created_at_server"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"OTP({self.phone})"


class EmailVerification(UUIDModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_verifications")
    email = models.EmailField()
    token_hash = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "auth_email_verifications"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["email", "status"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"EmailVerification({self.user_id}, {self.email})"


# ---------------------------------------------------------------------------
# User Device (for push notifications & offline sync)
# ---------------------------------------------------------------------------
class UserDevice(UUIDModel):
    PLATFORM_CHOICES = [("android", "Android"), ("ios", "iOS"), ("web", "Web")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    device_id = models.CharField(max_length=128, db_index=True)
    fcm_token = models.TextField(blank=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    app_version = models.CharField(max_length=20, blank=True)
    device_name = models.CharField(max_length=120, blank=True)
    os_version = models.CharField(max_length=64, blank=True)
    public_key = models.TextField(blank=True)
    notification_enabled = models.BooleanField(default=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Device-level sync metadata
    created_at_client = models.DateTimeField(null=True, blank=True)
    updated_at_client = models.DateTimeField(null=True, blank=True)
    created_at_server = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at_server = models.DateTimeField(auto_now=True, db_index=True)
    sync_status = models.CharField(
        max_length=24,
        choices=SyncableModel.SyncStatus.choices,
        default=SyncableModel.SyncStatus.SYNCED,
        db_index=True,
    )
    version = models.BigIntegerField(default=1)
    created_by_device_id = models.CharField(max_length=128, blank=True)
    last_modified_by_device_id = models.CharField(max_length=128, blank=True)

    class Meta:
        db_table = "auth_user_devices"
        unique_together = [("user", "device_id")]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["fcm_token"]),
            models.Index(fields=["updated_at_server"]),
        ]

    def __str__(self):
        return f"{self.user} / {self.platform} / {self.device_id[:12]}"


class UserSession(UUIDModel):
    """Per-device refresh-token/session tracking for multi-device JWT readiness."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        REVOKED = "revoked", "Revoked"
        EXPIRED = "expired", "Expired"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    device = models.ForeignKey(
        UserDevice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions",
    )
    refresh_jti = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    last_rotated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "auth_user_sessions"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["issued_at"]),
        ]

    def __str__(self):
        return f"Session({self.user_id}, {self.status})"
