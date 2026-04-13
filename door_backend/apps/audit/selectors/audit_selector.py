from apps.audit.models import AuditLog


class AuditSelector:
    @staticmethod
    def by_entity(entity_type: str, entity_id: str):
        return AuditLog.objects.filter(entity_type=entity_type, entity_id=entity_id).order_by("-created_at_server")
