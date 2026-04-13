from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers as nested_routers
from django.urls import path, include
from .views import (
    OrganizationViewSet,
    OrganizationMemberViewSet,
    EventViewSet,
    HouseholdViewSet,
    HouseholdMemberViewSet,
    AttendanceSessionViewSet,
    AttendanceRecordViewSet,
    VisitorLogViewSet,
    CheckpointViewSet,
    TripViewSet,
    TripCheckpointLogViewSet,
    GatherSessionViewSet,
    GatherParticipantViewSet,
    EmergencyCardViewSet,
    HajjTrackerProfileViewSet,
    MissingPersonCaseViewSet,
    MissingPersonSightingViewSet,
)

router = SimpleRouter()
router.register("households", HouseholdViewSet, basename="households")
router.register("household-members", HouseholdMemberViewSet, basename="household-members")
router.register("attendance-sessions", AttendanceSessionViewSet, basename="attendance-sessions")
router.register("attendance-records", AttendanceRecordViewSet, basename="attendance-records")
router.register("visitor-logs", VisitorLogViewSet, basename="visitor-logs")
router.register("checkpoints", CheckpointViewSet, basename="checkpoints")
router.register("trips", TripViewSet, basename="trips")
router.register("trip-checkpoint-logs", TripCheckpointLogViewSet, basename="trip-checkpoint-logs")
router.register("gather-sessions", GatherSessionViewSet, basename="gather-sessions")
router.register("gather-participants", GatherParticipantViewSet, basename="gather-participants")
router.register("emergency-cards", EmergencyCardViewSet, basename="emergency-cards")
router.register("hajj-profiles", HajjTrackerProfileViewSet, basename="hajj-profiles")
router.register("missing-person-cases", MissingPersonCaseViewSet, basename="missing-person-cases")
router.register("missing-person-sightings", MissingPersonSightingViewSet, basename="missing-person-sightings")

organization_router = SimpleRouter()
organization_router.register("", OrganizationViewSet, basename="organization")

org_router = nested_routers.NestedSimpleRouter(organization_router, "", lookup="org")
org_router.register("members", OrganizationMemberViewSet, basename="org-members")
org_router.register("events", EventViewSet, basename="org-events")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(organization_router.urls)),
    path("", include(org_router.urls)),
]
