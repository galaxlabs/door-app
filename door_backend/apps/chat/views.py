from rest_framework import viewsets
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer


class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        return ChatRoom.objects.filter(members__user=self.request.user).distinct()


class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatMessageSerializer
    filterset_fields = ["room", "type"]

    def get_queryset(self):
        return ChatMessage.objects.filter(
            room__members__user=self.request.user,
            is_deleted=False,
        ).select_related("sender").distinct()
