from apps.broadcast.models import BroadcastMessage


class BroadcastSelector:
    @staticmethod
    def messages_for_user(user):
        return BroadcastMessage.objects.filter(deliveries__user=user).distinct()
