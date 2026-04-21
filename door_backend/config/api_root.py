from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


class ApiV1RootView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {
                "ok": True,
                "name": "Door App API",
                "version": "v1",
                "docs": "/api/v1/docs/",
                "schema": "/api/v1/schema/",
                "redoc": "/api/v1/redoc/",
                "endpoints": {
                    "auth": "/api/v1/auth/",
                    "organizations": "/api/v1/organizations/",
                    "qr": "/api/v1/qr/",
                    "queues": "/api/v1/queues/",
                    "chat": "/api/v1/chat/",
                    "broadcast": "/api/v1/broadcast/",
                    "sync": "/api/v1/sync/",
                    "audit": "/api/v1/audit/",
                    "notifications": "/api/v1/notifications/",
                },
            }
        )

