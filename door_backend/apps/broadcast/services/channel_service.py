from apps.broadcast.models import BroadcastSubscription


class BroadcastChannelService:
    @staticmethod
    def subscribe(*, channel, user):
        return BroadcastSubscription.objects.get_or_create(channel=channel, user=user)

    @staticmethod
    def unsubscribe(*, channel, user):
        BroadcastSubscription.objects.filter(channel=channel, user=user).delete()
