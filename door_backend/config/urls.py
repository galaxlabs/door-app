from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

api_v1 = [
    path("auth/", include("apps.auth_identity.urls")),
    path("organizations/", include("apps.organizations.urls")),
    path("qr/", include("apps.qr_engine.urls")),
    path("queues/", include("apps.queue_control.urls")),
    path("chat/", include("apps.chat.urls")),
    path("broadcast/", include("apps.broadcast.urls")),
    path("sync/", include("apps.sync.urls")),
    path("audit/", include("apps.audit.urls")),
    path("notifications/", include("apps.notifications.urls")),
    # Schema
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
