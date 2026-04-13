from django.db import models
from django.conf import settings
from django.db.models import Q, F

from common.models import SoftDeleteModel


class Organization(SoftDeleteModel):
    TYPE_CHOICES = [
        ("organization", "Organization"),
        ("unit", "Unit"),
        ("branch", "Branch"),
    ]
    LOCALE_CHOICES = [("en", "English"), ("ar", "Arabic"), ("ur", "Urdu")]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("archived", "Archived"),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="organization")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="active", db_index=True)
    parent_organization = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="units",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_organizations",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_organizations",
    )
    logo = models.ImageField(upload_to="org_logos/", blank=True, null=True)
    description = models.TextField(blank=True)
    locale = models.CharField(max_length=5, choices=LOCALE_CHOICES, default="en")
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    settings = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "organizations"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["parent_organization"]),
            models.Index(fields=["updated_at_server"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=~Q(id=F("parent_organization")),
                name="org_parent_not_self",
            )
        ]

    def __str__(self):
        return self.name


class OrganizationMember(SoftDeleteModel):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("organization_admin", "Organization Admin"),
        ("manager", "Manager"),
        ("group_leader", "Group Leader"),
        ("staff", "Staff"),
        ("general_user", "General User"),
    ]
    STATUS_CHOICES = [
        ("invited", "Invited"),
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("left", "Left"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=24, choices=ROLE_CHOICES, default="general_user", db_index=True)
    membership_status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default="active",
        db_index=True,
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        db_table = "org_members"
        unique_together = [("organization", "user")]
        indexes = [
            models.Index(fields=["organization", "role"]),
            models.Index(fields=["user", "membership_status"]),
            models.Index(fields=["updated_at_server"]),
        ]

    def __str__(self):
        return f"{self.user} @ {self.organization} ({self.role})"


class Event(SoftDeleteModel):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("live", "Live"),
        ("ended", "Ended"),
        ("canceled", "Canceled"),
    ]
    EVENT_TYPE_CHOICES = [
        ("internal", "Internal"),
        ("public", "Public"),
        ("service", "Service"),
        ("custom", "Custom"),
    ]
    SCOPE_CHOICES = [
        ("organization", "Organization"),
        ("group", "Group"),
        ("public", "Public"),
        ("private", "Private"),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_events",
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=500, blank=True)
    location_data = models.JSONField(default=dict, blank=True)

    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default="internal")
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default="organization")
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    capacity = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "org_events"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["event_type", "scope"]),
            models.Index(fields=["starts_at"]),
            models.Index(fields=["updated_at_server"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(ends_at__isnull=True) | Q(starts_at__isnull=True) | Q(ends_at__gte=F("starts_at")),
                name="event_end_after_start",
            )
        ]

    def __str__(self):
        return f"{self.name} [{self.organization or 'global'}]"


class Group(SoftDeleteModel):
    TYPE_CHOICES = [
        ("staff", "Staff"),
        ("attendee", "Attendee"),
        ("vip", "VIP"),
        ("custom", "Custom"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("archived", "Archived"),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="groups",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="groups",
    )
    name = models.CharField(max_length=255)
    group_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="custom")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="active", db_index=True)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leading_groups",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "org_groups"
        unique_together = [("organization", "name")]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["event"]),
            models.Index(fields=["leader"]),
            models.Index(fields=["updated_at_server"]),
        ]

    def __str__(self):
        return f"{self.name} [{self.organization}]"


class GroupMember(SoftDeleteModel):
    ROLE_CHOICES = [
        ("group_leader", "Group Leader"),
        ("staff", "Staff"),
        ("general_user", "General User"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("muted", "Muted"),
        ("removed", "Removed"),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="group_memberships",
    )
    role = models.CharField(max_length=24, choices=ROLE_CHOICES, default="general_user", db_index=True)
    membership_status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default="active",
        db_index=True,
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        db_table = "org_group_members"
        unique_together = [("group", "user")]
        indexes = [
            models.Index(fields=["group", "role"]),
            models.Index(fields=["user", "membership_status"]),
            models.Index(fields=["updated_at_server"]),
        ]

    def __str__(self):
        return f"{self.user} @ {self.group} ({self.role})"


class Household(SoftDeleteModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="households",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="households",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="households",
    )
    name = models.CharField(max_length=255)
    family_code = models.CharField(max_length=64, db_index=True)
    head_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_households",
    )
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "org_households"
        unique_together = [("organization", "family_code")]
        indexes = [
            models.Index(fields=["organization", "family_code"]),
            models.Index(fields=["event"]),
            models.Index(fields=["group"]),
        ]


class HouseholdMember(SoftDeleteModel):
    RELATIONSHIP_CHOICES = [
        ("head", "Head"),
        ("spouse", "Spouse"),
        ("child", "Child"),
        ("parent", "Parent"),
        ("sibling", "Sibling"),
        ("guardian", "Guardian"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("missing", "Missing"),
        ("safe", "Safe"),
        ("inactive", "Inactive"),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="household_memberships",
    )
    relationship = models.CharField(max_length=16, choices=RELATIONSHIP_CHOICES, default="other")
    hierarchy_level = models.PositiveSmallIntegerField(default=0)
    is_guardian = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="active", db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "org_household_members"
        unique_together = [("household", "user")]
        indexes = [
            models.Index(fields=["household", "relationship"]),
            models.Index(fields=["user", "status"]),
        ]


class AttendanceSession(SoftDeleteModel):
    SESSION_TYPE_CHOICES = [
        ("attendance", "Attendance"),
        ("checkpoint", "Checkpoint"),
        ("gather", "Gather"),
    ]
    MODE_CHOICES = [
        ("manual", "Manual"),
        ("qr", "QR"),
        ("geo", "Geo"),
    ]
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("closed", "Closed"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="attendance_sessions")
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendance_sessions")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendance_sessions")
    title = models.CharField(max_length=255)
    session_type = models.CharField(max_length=16, choices=SESSION_TYPE_CHOICES, default="attendance")
    attendance_mode = models.CharField(max_length=16, choices=MODE_CHOICES, default="manual")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="draft", db_index=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "org_attendance_sessions"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["event"]),
            models.Index(fields=["group"]),
        ]


class AttendanceRecord(SoftDeleteModel):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
    ]
    METHOD_CHOICES = [
        ("manual", "Manual"),
        ("qr", "QR"),
        ("geo", "Geo"),
    ]

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendance_records")
    household_member = models.ForeignKey(
        HouseholdMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_records",
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="present", db_index=True)
    check_in_method = models.CharField(max_length=16, choices=METHOD_CHOICES, default="manual")
    checked_in_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "org_attendance_records"
        unique_together = [("session", "user")]
        indexes = [
            models.Index(fields=["session", "status"]),
            models.Index(fields=["user", "status"]),
        ]


class VisitorLog(SoftDeleteModel):
    STATUS_CHOICES = [
        ("arrived", "Arrived"),
        ("approved", "Approved"),
        ("denied", "Denied"),
        ("departed", "Departed"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="visitor_logs")
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name="visitor_logs")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="visitor_logs")
    host_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hosted_visitors",
    )
    visitor_name = models.CharField(max_length=255)
    visitor_phone = models.CharField(max_length=20, blank=True)
    purpose = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="arrived", db_index=True)
    arrived_at = models.DateTimeField(auto_now_add=True)
    departed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "org_visitor_logs"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["host_user"]),
            models.Index(fields=["arrived_at"]),
        ]


class Checkpoint(SoftDeleteModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="checkpoints")
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name="checkpoints")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="checkpoints")
    name = models.CharField(max_length=255)
    checkpoint_code = models.CharField(max_length=64, db_index=True)
    location_name = models.CharField(max_length=255, blank=True)
    sequence = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "org_checkpoints"
        unique_together = [("organization", "checkpoint_code")]
        indexes = [
            models.Index(fields=["organization", "sequence"]),
            models.Index(fields=["event"]),
            models.Index(fields=["group"]),
        ]


class Trip(SoftDeleteModel):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="trips")
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name="trips")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="trips")
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="draft", db_index=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "org_trips"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["event"]),
            models.Index(fields=["group"]),
        ]


class TripCheckpointLog(SoftDeleteModel):
    STATUS_CHOICES = [
        ("arrived", "Arrived"),
        ("departed", "Departed"),
        ("missed", "Missed"),
    ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="checkpoint_logs")
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.CASCADE, related_name="trip_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trip_checkpoint_logs")
    device_id = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="arrived", db_index=True)
    scanned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "org_trip_checkpoint_logs"
        indexes = [
            models.Index(fields=["trip", "status"]),
            models.Index(fields=["checkpoint", "status"]),
            models.Index(fields=["user", "scanned_at"]),
        ]


class GatherSession(SoftDeleteModel):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("closed", "Closed"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="gather_sessions")
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name="gather_sessions")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="gather_sessions")
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="draft", db_index=True)
    target_count = models.PositiveIntegerField(default=0)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "org_gather_sessions"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["event"]),
            models.Index(fields=["group"]),
        ]


class GatherParticipant(SoftDeleteModel):
    STATUS_CHOICES = [
        ("invited", "Invited"),
        ("joined", "Joined"),
        ("missing", "Missing"),
        ("safe", "Safe"),
    ]

    gather_session = models.ForeignKey(GatherSession, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="gather_participations")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="invited", db_index=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    last_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "org_gather_participants"
        unique_together = [("gather_session", "user")]
        indexes = [
            models.Index(fields=["gather_session", "status"]),
            models.Index(fields=["user", "status"]),
        ]


class EmergencyCard(SoftDeleteModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="emergency_cards")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="emergency_cards")
    blood_group = models.CharField(max_length=8, blank=True)
    allergies = models.TextField(blank=True)
    medical_notes = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=255)
    emergency_contact_phone = models.CharField(max_length=20)
    emergency_contact_relationship = models.CharField(max_length=64, blank=True)
    home_location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "org_emergency_cards"
        unique_together = [("organization", "user")]
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["user"]),
        ]


class HajjTrackerProfile(SoftDeleteModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("missing", "Missing"),
        ("safe", "Safe"),
        ("offline", "Offline"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="hajj_profiles")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="hajj_profiles")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hajj_profiles")
    package_name = models.CharField(max_length=255, blank=True)
    tent_number = models.CharField(max_length=64, blank=True)
    bus_number = models.CharField(max_length=64, blank=True)
    passport_last4 = models.CharField(max_length=8, blank=True)
    health_flags = models.JSONField(default=list, blank=True)
    is_group_lead = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="active", db_index=True)

    class Meta:
        db_table = "org_hajj_profiles"
        unique_together = [("organization", "user")]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["group"]),
            models.Index(fields=["is_group_lead"]),
        ]


class MissingPersonCase(SoftDeleteModel):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("located", "Located"),
        ("closed", "Closed"),
    ]
    PRIORITY_CHOICES = [
        ("normal", "Normal"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="missing_person_cases")
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name="missing_person_cases")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="missing_person_cases")
    subject_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="missing_person_cases",
    )
    title = models.CharField(max_length=255)
    subject_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="open", db_index=True)
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default="normal", db_index=True)
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opened_missing_person_cases",
    )
    last_seen_at = models.DateTimeField(null=True, blank=True)
    last_seen_notes = models.TextField(blank=True)
    last_seen_location = models.CharField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "org_missing_person_cases"
        indexes = [
            models.Index(fields=["organization", "status", "priority"]),
            models.Index(fields=["event"]),
            models.Index(fields=["group"]),
            models.Index(fields=["subject_user"]),
        ]


class MissingPersonSighting(SoftDeleteModel):
    case = models.ForeignKey(MissingPersonCase, on_delete=models.CASCADE, related_name="sightings")
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="missing_person_sightings",
    )
    note = models.TextField(blank=True)
    location_name = models.CharField(max_length=255, blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    confidence = models.PositiveSmallIntegerField(default=50)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "org_missing_person_sightings"
        indexes = [
            models.Index(fields=["case", "reported_at"]),
            models.Index(fields=["reported_by"]),
            models.Index(fields=["is_verified"]),
        ]
