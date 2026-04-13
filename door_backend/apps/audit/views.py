from rest_framework import generics
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(generics.ListAPIView):
    """GET /api/v1/audit/ — read-only audit trail (admins only)."""

    serializer_class = AuditLogSerializer
    filterset_fields = ["action", "entity_type", "entity_id", "organization", "user"]

    def get_queryset(self):
        user = self.request.user
        if user.role in ("super_admin",):
            return AuditLog.objects.all()
        # Org admins see their org's logs
        org_ids = list(
            user.memberships.filter(role="admin").values_list("organization_id", flat=True)
        )
        return AuditLog.objects.filter(organization_id__in=org_ids)
