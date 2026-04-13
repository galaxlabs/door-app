from django.utils import timezone

from apps.auth_identity.models import UserSession


class SessionService:
    @staticmethod
    def revoke_session(session: UserSession) -> UserSession:
        session.status = UserSession.Status.REVOKED
        session.revoked_at = timezone.now()
        session.save(update_fields=["status", "revoked_at"])
        return session

    @staticmethod
    def revoke_all_user_sessions(user) -> int:
        return UserSession.objects.filter(user=user, status=UserSession.Status.ACTIVE).update(
            status=UserSession.Status.REVOKED,
            revoked_at=timezone.now(),
        )
