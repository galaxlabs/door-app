from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User, OTP, UserDevice, EmailVerification, UserSession


class OTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, required=False)
    phone = serializers.CharField(max_length=20, required=False, write_only=True)

    def validate(self, attrs):
        phone_number = attrs.get("phone_number") or attrs.get("phone")
        if not phone_number:
            raise serializers.ValidationError({"phone_number": _("Phone number is required.")})
        attrs["phone_number"] = phone_number.strip()
        return attrs


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, required=False)
    phone = serializers.CharField(max_length=20, required=False, write_only=True)
    code = serializers.CharField(max_length=8)

    def validate(self, attrs):
        phone_number = attrs.get("phone_number") or attrs.get("phone")
        if not phone_number:
            raise serializers.ValidationError({"phone_number": _("Phone number is required.")})
        attrs["phone_number"] = phone_number.strip()
        otp = (
            OTP.objects.filter(
                phone=attrs["phone_number"],
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
    phone = serializers.CharField(source="phone_number", read_only=True)
    is_profile_setup = serializers.SerializerMethodField()
    profile_setup_issues = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "public_id", "anonymous_id",
            "phone", "phone_number", "email", "full_name", "avatar",
            "intro", "age",
            "role", "locale", "timezone",
            "is_phone_verified", "is_email_verified", "status", "is_active",
            "is_profile_setup", "profile_setup_issues",
            "default_organization", "created_at_server", "updated_at_server",
        ]
        read_only_fields = [
            "id", "public_id", "anonymous_id",
            "phone", "phone_number", "email", "is_phone_verified", "is_email_verified",
            "status",
            "is_profile_setup", "profile_setup_issues",
            "created_at_server", "updated_at_server",
        ]

    def validate_age(self, value):
        if value is None:
            return value
        if value < 1 or value > 120:
            raise serializers.ValidationError(_("Age must be between 1 and 120."))
        return value

    def validate_intro(self, value):
        return (value or "").strip()

    def get_is_profile_setup(self, obj: User) -> bool:
        return obj.is_profile_setup

    def get_profile_setup_issues(self, obj: User) -> list[str]:
        return obj.profile_setup_issues()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["email", "phone_number", "full_name", "password"]

    def validate_email(self, value):
        email = User.objects._normalize_email_value(value)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(_("An account with this email already exists."))
        return email

    def validate_phone_number(self, value):
        phone_number = User.objects._normalize_phone_number(value)
        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError(_("An account with this phone number already exists."))
        return phone_number

    def validate_full_name(self, value):
        full_name = value.strip()
        if not full_name:
            raise serializers.ValidationError(_("Full name is required."))
        return full_name

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class PasswordLoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        identifier = attrs["identifier"].strip()
        password = attrs["password"]
        normalized_email = User.objects._normalize_email_value(identifier)
        normalized_phone_number = User.objects._normalize_phone_number(identifier)

        user = User.objects.filter(email=normalized_email).first()
        if user is None:
            user = User.objects.filter(phone_number=normalized_phone_number).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError(_("Invalid login credentials."))
        if not user.is_active or user.status in {User.AccountStatus.SUSPENDED, User.AccountStatus.DISABLED}:
            raise serializers.ValidationError(_("This account is not allowed to sign in."))

        attrs["user"] = user
        return attrs


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
