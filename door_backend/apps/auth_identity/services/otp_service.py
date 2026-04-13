from datetime import timedelta
import random
import string

from django.utils import timezone

from apps.auth_identity.models import OTP


class OTPService:
    @staticmethod
    def generate_code(length: int = 6) -> str:
        return "".join(random.choices(string.digits, k=length))

    @classmethod
    def issue_otp(cls, phone: str, channel: str = "sms", ip: str = "", user_agent: str = "") -> OTP:
        code = cls.generate_code()
        return OTP.objects.create(
            phone=phone,
            code=code,
            channel=channel,
            expires_at=timezone.now() + timedelta(minutes=10),
            request_ip=ip or None,
            request_user_agent=user_agent,
        )

    @staticmethod
    def mark_verified(otp: OTP) -> OTP:
        otp.used = True
        otp.status = OTP.Status.VERIFIED
        otp.consumed_at = timezone.now()
        otp.save(update_fields=["used", "status", "consumed_at"])
        return otp
