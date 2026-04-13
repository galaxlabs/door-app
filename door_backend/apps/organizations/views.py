from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Organization,
    OrganizationMember,
    Event,
    Household,
    HouseholdMember,
    AttendanceSession,
    AttendanceRecord,
    VisitorLog,
    Checkpoint,
    Trip,
    TripCheckpointLog,
    GatherSession,
    GatherParticipant,
    EmergencyCard,
    HajjTrackerProfile,
    MissingPersonCase,
    MissingPersonSighting,
)
from .serializers import (
    OrganizationSerializer,
    OrganizationMemberSerializer,
    EventSerializer,
    HouseholdSerializer,
    HouseholdMemberSerializer,
    AttendanceSessionSerializer,
    AttendanceRecordSerializer,
    VisitorLogSerializer,
    CheckpointSerializer,
    TripSerializer,
    TripCheckpointLogSerializer,
    GatherSessionSerializer,
    GatherParticipantSerializer,
    EmergencyCardSerializer,
    HajjTrackerProfileSerializer,
    MissingPersonCaseSerializer,
    MissingPersonSightingSerializer,
)


class OrganizationScopedQuerySetMixin:
    organization_lookup = "organization"

    def get_queryset(self):
        lookup = f"{self.organization_lookup}__members__user"
        return self.queryset.filter(**{lookup: self.request.user}).distinct()


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["type", "is_active"]

    def get_queryset(self):
        return Organization.objects.filter(
            members__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        org = serializer.save(owner=self.request.user, created_by=self.request.user)
        OrganizationMember.objects.create(
            organization=org, user=self.request.user, role="owner"
        )


class OrganizationMemberViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationMemberSerializer

    def get_queryset(self):
        return OrganizationMember.objects.filter(
            organization_id=self.kwargs["org_pk"]
        )

    def perform_create(self, serializer):
        from apps.organizations.models import Organization
        org = Organization.objects.get(pk=self.kwargs["org_pk"])
        serializer.save(organization=org, invited_by=self.request.user)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    filterset_fields = ["status", "organization"]

    def get_queryset(self):
        return Event.objects.filter(
            organization__members__user=self.request.user
        ).distinct()


class HouseholdViewSet(OrganizationScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = HouseholdSerializer
    queryset = Household.objects.all()
    filterset_fields = ["organization", "event", "group"]


class HouseholdMemberViewSet(viewsets.ModelViewSet):
    serializer_class = HouseholdMemberSerializer
    queryset = HouseholdMember.objects.select_related("household")
    filterset_fields = ["household", "status", "relationship"]

    def get_queryset(self):
        return HouseholdMember.objects.filter(
            household__organization__members__user=self.request.user
        ).distinct()


class AttendanceSessionViewSet(OrganizationScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = AttendanceSessionSerializer
    queryset = AttendanceSession.objects.all()
    filterset_fields = ["organization", "event", "group", "status", "session_type"]


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceRecordSerializer
    queryset = AttendanceRecord.objects.select_related("session")
    filterset_fields = ["session", "user", "status"]

    def get_queryset(self):
        return AttendanceRecord.objects.filter(
            session__organization__members__user=self.request.user
        ).distinct()


class VisitorLogViewSet(OrganizationScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = VisitorLogSerializer
    queryset = VisitorLog.objects.all()
    filterset_fields = ["organization", "event", "group", "status"]


class CheckpointViewSet(OrganizationScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = CheckpointSerializer
    queryset = Checkpoint.objects.all()
    filterset_fields = ["organization", "event", "group", "is_active"]


class TripViewSet(OrganizationScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = TripSerializer
    queryset = Trip.objects.all()
    filterset_fields = ["organization", "event", "group", "status"]


class TripCheckpointLogViewSet(viewsets.ModelViewSet):
    serializer_class = TripCheckpointLogSerializer
    queryset = TripCheckpointLog.objects.select_related("trip")
    filterset_fields = ["trip", "checkpoint", "user", "status"]

    def get_queryset(self):
        return TripCheckpointLog.objects.filter(
            trip__organization__members__user=self.request.user
        ).distinct()


class GatherSessionViewSet(OrganizationScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = GatherSessionSerializer
    queryset = GatherSession.objects.all()
    filterset_fields = ["organization", "event", "group", "status"]


class GatherParticipantViewSet(viewsets.ModelViewSet):
    serializer_class = GatherParticipantSerializer
    queryset = GatherParticipant.objects.select_related("gather_session")
    filterset_fields = ["gather_session", "user", "status"]

    def get_queryset(self):
        return GatherParticipant.objects.filter(
            gather_session__organization__members__user=self.request.user
        ).distinct()


class EmergencyCardViewSet(OrganizationScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = EmergencyCardSerializer
    queryset = EmergencyCard.objects.all()
    filterset_fields = ["organization", "user", "is_active"]


class HajjTrackerProfileViewSet(OrganizationScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = HajjTrackerProfileSerializer
    queryset = HajjTrackerProfile.objects.all()
    filterset_fields = ["organization", "group", "user", "status", "is_group_lead"]


class MissingPersonCaseViewSet(OrganizationScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = MissingPersonCaseSerializer
    queryset = MissingPersonCase.objects.all()
    filterset_fields = ["organization", "event", "group", "status", "priority"]

    def perform_create(self, serializer):
        serializer.save(opened_by=self.request.user)


class MissingPersonSightingViewSet(viewsets.ModelViewSet):
    serializer_class = MissingPersonSightingSerializer
    queryset = MissingPersonSighting.objects.select_related("case")
    filterset_fields = ["case", "is_verified"]

    def get_queryset(self):
        return MissingPersonSighting.objects.filter(
            case__organization__members__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
