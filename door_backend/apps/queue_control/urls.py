from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from .views import QueueViewSet, QueueTicketViewSet

router = DefaultRouter()
router.register("", QueueViewSet, basename="queue")

ticket_router = nested_routers.NestedDefaultRouter(router, "", lookup="queue")
ticket_router.register("tickets", QueueTicketViewSet, basename="queue-tickets")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(ticket_router.urls)),
]
