from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BroadcastChannelViewSet, BroadcastMessageViewSet

router = DefaultRouter()
router.register("channels", BroadcastChannelViewSet, basename="broadcast-channel")
router.register("messages", BroadcastMessageViewSet, basename="broadcast-message")

urlpatterns = [path("", include(router.urls))]
