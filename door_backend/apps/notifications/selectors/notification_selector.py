from apps.notifications.models import Notification


class NotificationSelector:
    @staticmethod
    def unread_for_user(user):
        return Notification.objects.filter(user=user, state="unread", is_deleted=False).order_by("-created_at_server")
