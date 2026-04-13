import re

from django.conf import settings


class CNICVerificationService:
    """CNIC verification service with optional bypass mode."""

    CNIC_REGEX = re.compile(r"^\d{5}-?\d{7}-?\d$")

    @classmethod
    def verify(cls, cnic: str) -> dict:
        normalized = (cnic or "").strip()

        if settings.BYPASS_CNIC_VERIFICATION:
            return {
                "is_valid": True,
                "normalized": normalized,
                "bypassed": True,
                "message": "CNIC validation bypassed by configuration.",
            }

        is_valid = bool(cls.CNIC_REGEX.match(normalized))
        return {
            "is_valid": is_valid,
            "normalized": normalized,
            "bypassed": False,
            "message": "OK" if is_valid else "Invalid CNIC format.",
        }
