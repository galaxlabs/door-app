import random
import string
import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import OTP, User, UserDevice
from .serializers import (
    OTPRequestSerializer,
    OTPVerifySerializer,
    UserSerializer,
    UserDeviceSerializer,
)


logger = logging.getLogger(__name__)


def _generate_otp(length=6):
    return "".join(random.choices(string.digits, k=length))


class OTPRequestView(APIView):
    """POST /api/v1/auth/otp/request/ — send OTP to phone."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = OTPRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        phone = ser.validated_data["phone"]

        code = _generate_otp()
        OTP.objects.create(
            phone=phone,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        # TODO: integrate real SMS gateway (Twilio / local)
        # sms_service.send(phone, f"Your Door OTP: {code}")

        logger.info("DEV OTP for %s is %s", phone, code)
        payload = {"ok": True, "message": "OTP sent."}
        if settings.DEBUG:
            payload["otp_code"] = code
        return Response(payload)


class OTPVerifyView(APIView):
    """POST /api/v1/auth/otp/verify/ — verify OTP, return JWT pair."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get("phone", "")
        if settings.BYPASS_OTP_VERIFICATION:
            if not phone:
                return Response({"detail": "phone is required."}, status=status.HTTP_400_BAD_REQUEST)
            otp = None
        else:
            ser = OTPVerifySerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            otp = ser.validated_data["otp"]
            phone = otp.phone
            otp.used = True
            otp.save(update_fields=["used"])

        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={"is_phone_verified": True},
        )
        if not created and not user.is_phone_verified:
            user.is_phone_verified = True
            user.save(update_fields=["is_phone_verified"])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "ok": True,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": str(user.id),
                "is_new_user": created,
            }
        )


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/auth/me/"""

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class DeviceRegisterView(generics.CreateAPIView):
    """POST /api/v1/auth/devices/ — register a device for push/sync."""

    serializer_class = UserDeviceSerializer

    def perform_create(self, serializer):
        UserDevice.objects.update_or_create(
            user=self.request.user,
            device_id=serializer.validated_data["device_id"],
            defaults={
                "fcm_token": serializer.validated_data.get("fcm_token", ""),
                "platform": serializer.validated_data["platform"],
                "app_version": serializer.validated_data.get("app_version", ""),
                "is_active": True,
            },
        )
