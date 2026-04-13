from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import User, OTP, UserDevice, EmailVerification, UserSession


class OTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=8)

    def validate(self, attrs):
        otp = (
            OTP.objects.filter(
                phone=attrs["phone"],
                code=attrs["code"],
                used=False,
                expires_at__gt=timezone.now(),
            )
            .order_by("-created_at_server")
            .first()
        )
        if not otp:
            raise serializers.ValidationError(_("Invalid or expired OTP."))
        attrs["otp"] = otp
        return attrs


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user_id = serializers.UUIDField()
    is_new_user = serializers.BooleanField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "public_id", "anonymous_id",
            "phone", "email", "full_name", "avatar",
            "role", "locale", "timezone",
            "is_phone_verified", "is_email_verified", "is_active",
            "default_organization", "created_at_server", "updated_at_server",
        ]
        read_only_fields = [
            "id", "public_id", "anonymous_id",
            "phone", "is_phone_verified", "is_email_verified",
            "created_at_server", "updated_at_server",
        ]


class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDevice
        fields = [
            "id", "device_id", "platform", "app_version", "device_name", "os_version",
            "fcm_token", "notification_enabled", "is_active", "last_seen",
        ]
        read_only_fields = ["id", "last_seen"]


class EmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerification
        fields = ["id", "user", "email", "status", "expires_at", "verified_at", "created_at"]
        read_only_fields = ["id", "status", "verified_at", "created_at"]


class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = ["id", "user", "device", "status", "issued_at", "expires_at", "last_rotated_at"]
        read_only_fields = fields
