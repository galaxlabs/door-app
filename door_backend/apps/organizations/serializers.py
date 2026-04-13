from rest_framework import serializers
from .models import (
    Organization,
    OrganizationMember,
    Event,
    Group,
    GroupMember,
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


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id", "name", "slug", "type", "status", "parent_organization",
            "owner", "created_by", "logo", "description",
            "locale", "website", "is_active", "settings", "metadata",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = [
            "id",
            "owner",
            "created_by",
            "created_at_server",
            "updated_at_server",
        ]


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = OrganizationMember
        fields = [
            "id", "organization", "user", "user_name", "user_phone",
            "role", "membership_status", "joined_at", "invited_by",
        ]
        read_only_fields = ["id", "joined_at"]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id", "organization", "created_by", "name", "description",
            "location", "location_data", "event_type", "scope",
            "starts_at", "ends_at", "status", "capacity", "metadata",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            "id", "organization", "event", "name", "group_type", "status",
            "leader", "metadata", "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class GroupMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = GroupMember
        fields = [
            "id", "group", "user", "user_name", "role",
            "membership_status", "joined_at", "added_by",
        ]
        read_only_fields = ["id", "joined_at"]


class HouseholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Household
        fields = [
            "id", "organization", "event", "group", "name", "family_code",
            "head_user", "notes", "metadata", "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class HouseholdMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseholdMember
        fields = [
            "id", "household", "user", "relationship", "hierarchy_level",
            "is_guardian", "status", "notes", "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class AttendanceSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSession
        fields = [
            "id", "organization", "event", "group", "title", "session_type",
            "attendance_mode", "status", "starts_at", "ends_at", "metadata",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = [
            "id", "session", "user", "household_member", "status",
            "check_in_method", "checked_in_at", "notes",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "checked_in_at", "created_at_server", "updated_at_server"]


class VisitorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorLog
        fields = [
            "id", "organization", "event", "group", "host_user", "visitor_name",
            "visitor_phone", "purpose", "status", "arrived_at", "departed_at",
            "metadata", "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "arrived_at", "created_at_server", "updated_at_server"]


class CheckpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkpoint
        fields = [
            "id", "organization", "event", "group", "name", "checkpoint_code",
            "location_name", "sequence", "is_active", "metadata",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = [
            "id", "organization", "event", "group", "title", "status",
            "starts_at", "ends_at", "metadata",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class TripCheckpointLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripCheckpointLog
        fields = [
            "id", "trip", "checkpoint", "user", "device_id", "status",
            "scanned_at", "notes", "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "scanned_at", "created_at_server", "updated_at_server"]


class GatherSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatherSession
        fields = [
            "id", "organization", "event", "group", "title", "status",
            "target_count", "starts_at", "ends_at", "notes",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class GatherParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatherParticipant
        fields = [
            "id", "gather_session", "user", "status", "last_seen_at",
            "last_lat", "last_lng", "notes", "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class EmergencyCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyCard
        fields = [
            "id", "organization", "user", "blood_group", "allergies",
            "medical_notes", "emergency_contact_name", "emergency_contact_phone",
            "emergency_contact_relationship", "home_location", "is_active",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class HajjTrackerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HajjTrackerProfile
        fields = [
            "id", "organization", "group", "user", "package_name", "tent_number",
            "bus_number", "passport_last4", "health_flags", "is_group_lead",
            "status", "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "created_at_server", "updated_at_server"]


class MissingPersonCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissingPersonCase
        fields = [
            "id", "organization", "event", "group", "subject_user", "title",
            "subject_name", "status", "priority", "opened_by", "last_seen_at",
            "last_seen_notes", "last_seen_location", "contact_phone", "metadata",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "opened_by", "created_at_server", "updated_at_server"]


class MissingPersonSightingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissingPersonSighting
        fields = [
            "id", "case", "reported_by", "note", "location_name",
            "reported_at", "confidence", "is_verified",
            "created_at_server", "updated_at_server",
        ]
        read_only_fields = ["id", "reported_by", "reported_at", "created_at_server", "updated_at_server"]
