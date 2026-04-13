"""Audit logging middleware — records mutating HTTP requests."""
import json
from django.utils.deprecation import MiddlewareMixin


class AuditMiddleware(MiddlewareMixin):
    TRACKED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    def process_response(self, request, response):
        if request.method not in self.TRACKED_METHODS:
            return response
        if not request.path.startswith("/api/"):
            return response
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return response
        try:
            from apps.audit.models import AuditLog

            body = {}
            if request.content_type == "application/json":
                try:
                    body = json.loads(request.body)
                except Exception:
                    pass
            # strip sensitive fields
            for field in ("password", "token", "secret", "otp"):
                body.pop(field, None)

            AuditLog.objects.create(
                user=request.user,
                action=f"{request.method} {request.path}",
                payload=body,
                ip_address=_get_client_ip(request),
            )
        except Exception:
            pass
        return response


def _get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")
