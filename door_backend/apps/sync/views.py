from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import SyncUploadSerializer, SyncPullSerializer, ConflictLogSerializer
from .engine import process_upload_batch, get_delta
from .models import ConflictLog


class SyncUploadView(APIView):
    """POST /api/v1/sync/upload/ — push offline operations to server."""

    def post(self, request):
        ser = SyncUploadSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        result = process_upload_batch(
            user=request.user,
            device_id=ser.validated_data["device_id"],
            operations=ser.validated_data["operations"],
        )
        return Response({"ok": True, **result})


class SyncPullView(APIView):
    """POST /api/v1/sync/pull/ — pull server delta since last sync."""

    def post(self, request):
        ser = SyncPullSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        result = get_delta(
            user=request.user,
            device_id=ser.validated_data["device_id"],
            since=ser.validated_data.get("since", ""),
            entity_types=ser.validated_data["entity_types"],
        )
        return Response(result)


class SyncConflictListView(APIView):
    """GET /api/v1/sync/conflicts/ — list unresolved conflicts for user."""

    def get(self, request):
        qs = ConflictLog.objects.filter(user=request.user, resolved_at__isnull=True)
        return Response(ConflictLogSerializer(qs, many=True).data)
