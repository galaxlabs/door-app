from django.urls import re_path
from .consumers import BroadcastConsumer

websocket_urlpatterns = [
    re_path(r"ws/broadcast/(?P<channel_id>[0-9a-f-]+)/$", BroadcastConsumer.as_asgi()),
]
