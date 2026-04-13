from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.auth_identity.models import User
from apps.qr_engine.models import InteractionRecord

from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer, ChatMessageStatusUpdateSerializer
from .services import ChatMessageService, ChatRoomService


class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    filterset_fields = ["organization", "group", "interaction", "type", "status"]

    def get_queryset(self):
        return ChatRoom.objects.filter(members__user=self.request.user).distinct()

    def perform_create(self, serializer):
        member_user_ids = serializer.validated_data.pop("member_user_ids", [])
        room = serializer.save(created_by=self.request.user)
        ChatRoomService.ensure_member(room=room, user=self.request.user, role="admin")
        for member in User.objects.filter(id__in=member_user_ids):
            ChatRoomService.ensure_member(room=room, user=member, role="member")

    @action(detail=False, methods=["post"], url_path="ensure-direct")
    def ensure_direct(self, request):
        other_user = User.objects.get(pk=request.data.get("user_id"))
        room = ChatRoomService.ensure_direct_room(creator=request.user, other_user=other_user)
        return Response(ChatRoomSerializer(room).data)

    @action(detail=False, methods=["post"], url_path="ensure-interaction")
    def ensure_interaction(self, request):
        interaction = InteractionRecord.objects.select_related("initiated_by", "template", "qr_entity").get(
            pk=request.data.get("interaction_id")
        )
        members = list(User.objects.filter(id__in=request.data.get("member_user_ids", [])))
        room = ChatRoomService.ensure_interaction_room(
            interaction=interaction,
            owner=request.user,
            members=members,
        )
        return Response(ChatRoomSerializer(room).data)

    @action(detail=True, methods=["get", "post"], url_path="messages")
    def messages(self, request, pk=None):
        room = self.get_object()
        if request.method == "GET":
            queryset = room.messages.filter(is_deleted=False).select_related("sender")
            return Response(ChatMessageSerializer(queryset, many=True).data)

        message = ChatMessageService.send_message(
            room=room,
            sender=request.user,
            msg_type=request.data.get("type", "text"),
            content=request.data.get("content", ""),
            client_id=request.data.get("client_id", ""),
            sender_device_id=request.data.get("sender_device_id", ""),
        )
        return Response(ChatMessageSerializer(message).data, status=status.HTTP_201_CREATED)


class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatMessageSerializer
    filterset_fields = ["room", "type"]

    def get_queryset(self):
        return ChatMessage.objects.filter(
            room__members__user=self.request.user,
            is_deleted=False,
        ).select_related("sender").distinct()

    @action(detail=True, methods=["post"], url_path="status")
    def update_status(self, request, pk=None):
        message = self.get_object()
        serializer = ChatMessageStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ChatMessageService.update_status(
            message=message,
            user=request.user,
            status=serializer.validated_data["status"],
            status_device_id=serializer.validated_data.get("status_device_id", ""),
        )
        message.refresh_from_db()
        return Response(ChatMessageSerializer(message).data)
