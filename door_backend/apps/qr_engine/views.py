from django.db import transaction
from rest_framework import viewsets, views, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import QRCode, ScanToken, QROwnerMember, QRAlert
from .serializers import (
    QRCodeSerializer,
    QRScanSerializer,
    ScanTokenSerializer,
    QROwnerMemberSerializer,
    QRAlertRespondSerializer,
    QRAlertSerializer,
)
from .services.owner_notification_service import QROwnerNotificationService


class QRCodeViewSet(viewsets.ModelViewSet):
    serializer_class = QRCodeSerializer
    filterset_fields = ["organization", "event", "payload_type", "is_active"]

    def get_queryset(self):
        return QRCode.objects.filter(
            organization__members__user=self.request.user
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


class QRScanView(views.APIView):
    """POST /api/v1/qr/scan/ — scan a QR code, receive token + action."""

    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        ser = QRScanSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        token_obj = ser.save()
        return Response(ScanTokenSerializer(token_obj).data, status=status.HTTP_201_CREATED)


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
