from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, views, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from apps.organizations.models import Event, Group, Organization
from apps.queue_control.models import Queue

from .models import (
    InteractionTemplate,
    TemplateField,
    TemplateWorkflowState,
    TemplateAction,
    NotificationRule,
    InteractionRecord,
    QRCode,
    ScanToken,
    QROwnerMember,
    QRAlert,
)
from .serializers import (
    InteractionTemplateSerializer,
    TemplateFieldSerializer,
    TemplateWorkflowStateSerializer,
    TemplateActionSerializer,
    NotificationRuleSerializer,
    InteractionRecordSerializer,
    InteractionActionSerializer,
    InteractionAuditLogSerializer,
    TemplatePackSeedSerializer,
    TemplatePackAdminSetupSerializer,
    QRCodeRuntimeActionSerializer,
    QRCodeSerializer,
    QRScanSerializer,
    ScanTokenSerializer,
    QROwnerMemberSerializer,
    QRAlertRespondSerializer,
    QRAlertSerializer,
)
from .services.interaction_service import InteractionRuntimeService
from .services.pack_runtime_service import TemplatePackRuntimeService
from .services.owner_notification_service import QROwnerNotificationService
from .services.template_pack_service import TemplatePackService


class InteractionTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = InteractionTemplateSerializer
    queryset = InteractionTemplate.objects.all().order_by("name", "version")
    filterset_fields = ["category", "is_public", "supports_offline"]


class TemplateFieldViewSet(viewsets.ModelViewSet):
    serializer_class = TemplateFieldSerializer
    queryset = TemplateField.objects.select_related("template").all().order_by("template_id", "field_key")
    filterset_fields = ["template", "field_type", "is_required"]


class TemplateWorkflowStateViewSet(viewsets.ModelViewSet):
    serializer_class = TemplateWorkflowStateSerializer
    queryset = TemplateWorkflowState.objects.select_related("template").all().order_by("template_id", "order")
    filterset_fields = ["template", "state_type", "is_initial", "is_final"]


class TemplateActionViewSet(viewsets.ModelViewSet):
    serializer_class = TemplateActionSerializer
    queryset = TemplateAction.objects.select_related("template", "source_state", "target_state").all().order_by("template_id", "action_key")
    filterset_fields = ["template", "role_required", "source_state", "target_state"]


class NotificationRuleViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationRuleSerializer
    queryset = NotificationRule.objects.select_related("template").all().order_by("template_id", "trigger_event")
    filterset_fields = ["template", "trigger_event", "audience_type", "channel", "priority"]


class QRCodeViewSet(viewsets.ModelViewSet):
    serializer_class = QRCodeSerializer
    filterset_fields = ["organization", "event", "payload_type", "is_active", "template", "purpose", "owner_type"]

    def get_queryset(self):
        return QRCode.objects.filter(
            Q(organization__members__user=self.request.user) | Q(created_by=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get", "post"], url_path="owner-members")
    def owner_members(self, request, pk=None):
        qr = self.get_object()

        if request.method == "GET":
            qs = qr.owner_members.filter(is_active=True).order_by("priority", "created_at_server")
            return Response(QROwnerMemberSerializer(qs, many=True).data)

        if qr.created_by_id != request.user.id and qr.organization and not qr.organization.members.filter(
            user=request.user, role__in=["owner", "organization_admin", "manager"], membership_status="active"
        ).exists():
            raise PermissionDenied("Only owner/admin can add QR members.")

        ser = QROwnerMemberSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(qr_code=qr, owner=request.user)
        return Response(ser.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="runtime-action")
    def runtime_action(self, request, pk=None):
        qr = self.get_object()
        serializer = QRCodeRuntimeActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = TemplatePackRuntimeService.execute_qr_runtime_action(
                qr_code=qr,
                operation=serializer.validated_data["operation"],
                actor=request.user,
                actor_device_id=serializer.validated_data.get("device_id", ""),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


class InteractionRecordViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InteractionRecordSerializer
    filterset_fields = ["template", "status", "current_state", "qr_entity"]

    def get_queryset(self):
        return (
            InteractionRecord.objects.select_related(
                "template",
                "qr_entity",
                "scan",
                "initiated_by",
                "current_state",
            )
            .filter(
                Q(qr_entity__organization__members__user=self.request.user)
                | Q(qr_entity__created_by=self.request.user)
                | Q(initiated_by=self.request.user)
            )
            .distinct()
        )

    @action(detail=True, methods=["get"], url_path="audit-logs")
    def audit_logs(self, request, pk=None):
        interaction = self.get_object()
        queryset = interaction.audit_logs.select_related("actor", "from_state", "to_state").all()
        return Response(InteractionAuditLogSerializer(queryset, many=True).data)

    @action(detail=True, methods=["post"], url_path="actions")
    def actions(self, request, pk=None):
        interaction = self.get_object()
        serializer = InteractionActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            updated_interaction = InteractionRuntimeService.apply_action(
                interaction=interaction,
                action_key=serializer.validated_data["action_key"],
                actor=request.user,
                device_id=serializer.validated_data.get("device_id", ""),
                payload_json=serializer.validated_data.get("payload_json", {}),
            )
        except PermissionError as exc:
            raise PermissionDenied(str(exc))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(InteractionRecordSerializer(updated_interaction).data)


class QRScanView(views.APIView):
    """POST /api/v1/qr/scan/ — scan a QR code, receive token + action."""

    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        ser = QRScanSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        token_obj = ser.save()
        return Response(ScanTokenSerializer(token_obj).data, status=status.HTTP_201_CREATED)


class TemplatePackCatalogView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"packs": TemplatePackService.catalog()})


class TemplatePackSeedView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TemplatePackSeedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        templates = TemplatePackService.seed_packs(serializer.validated_data["pack_keys"])
        return Response(
            {
                "templates": InteractionTemplateSerializer(templates, many=True).data,
            }
        )


class TemplatePackAdminSetupView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TemplatePackAdminSetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        organization = Organization.objects.filter(pk=validated.get("organization")).first() if validated.get("organization") else None
        event = Event.objects.filter(pk=validated.get("event")).first() if validated.get("event") else None
        group = Group.objects.filter(pk=validated.get("group")).first() if validated.get("group") else None
        queue = Queue.objects.filter(pk=validated.get("queue")).first() if validated.get("queue") else None
        template, qr_code, _ = TemplatePackService.admin_setup(
            pack_key=validated["pack_key"],
            created_by=request.user,
            name=validated["name"],
            organization=organization,
            event=event,
            group=group,
            queue=queue,
            owner_type=validated.get("owner_type", ""),
            owner_id=validated.get("owner_id", ""),
            metadata_json=validated.get("metadata_json", {}),
        )
        definition = TemplatePackService.get_definition(validated["pack_key"])
        return Response(
            {
                "template": InteractionTemplateSerializer(template).data,
                "qr_code": QRCodeSerializer(qr_code).data,
                "admin_setup_flow": definition["schema_json"]["admin_setup_flow"],
                "minimal_ui_requirements": definition["schema_json"]["minimal_ui_requirements"],
            },
            status=status.HTTP_201_CREATED,
        )


class ScanTokenRedeemView(views.APIView):
    """POST /api/v1/qr/token/redeem/ — redeem a scan token."""

    def post(self, request):
        token_str = request.data.get("token")
        try:
            from django.utils import timezone
            token_obj = ScanToken.objects.select_for_update().get(
                token=token_str, status="issued"
            )
        except ScanToken.DoesNotExist:
            return Response({"detail": "Invalid or already-used token."}, status=status.HTTP_400_BAD_REQUEST)

        from django.utils import timezone
        if timezone.now() > token_obj.expires_at:
            token_obj.status = "expired"
            token_obj.save(update_fields=["status"])
            return Response({"detail": "Token expired."}, status=status.HTTP_400_BAD_REQUEST)

        token_obj.status = "redeemed"
        token_obj.redeemed_at = timezone.now()
        token_obj.redeemed_by = request.user if request.user.is_authenticated else None
        token_obj.save(update_fields=["status", "redeemed_at", "redeemed_by"])
        return Response(ScanTokenSerializer(token_obj).data)


class QRAlertRespondView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, alert_id):
        try:
            alert = QRAlert.objects.select_for_update().get(pk=alert_id)
        except QRAlert.DoesNotExist:
            return Response({"detail": "Alert not found."}, status=status.HTTP_404_NOT_FOUND)

        ser = QRAlertRespondSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        member_id = ser.validated_data["member_id"]
        response_status = ser.validated_data["response_status"]
        response_note = ser.validated_data.get("response_note", "")

        recipient = alert.recipients.select_related("member").filter(member_id=member_id).first()
        if not recipient:
            return Response({"detail": "Alert recipient not found."}, status=status.HTTP_404_NOT_FOUND)

        is_owner = alert.qr_code.created_by_id == request.user.id
        is_assigned_member = recipient.member.member_user_id == request.user.id
        if not (is_owner or is_assigned_member):
            raise PermissionDenied("You are not allowed to respond for this recipient.")

        QROwnerNotificationService.respond(
            alert=alert,
            member_id=member_id,
            response_status=response_status,
            response_note=response_note,
        )
        alert.refresh_from_db()
        return Response(QRAlertSerializer(alert).data)
