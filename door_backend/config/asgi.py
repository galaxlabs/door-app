import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

django_asgi_app = get_asgi_application()

from common.ws_middleware import JWTAuthMiddlewareStack  # noqa: E402 (needs Django setup first)
import apps.queue_control.routing as queue_routing
import apps.chat.routing as chat_routing
import apps.broadcast.routing as broadcast_routing

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddlewareStack(
                URLRouter(
                    queue_routing.websocket_urlpatterns
                    + chat_routing.websocket_urlpatterns
                    + broadcast_routing.websocket_urlpatterns
                )
            )
        ),
    }
)
