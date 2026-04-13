from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QRCodeViewSet, QRScanView, ScanTokenRedeemView, QRAlertRespondView

router = DefaultRouter()
router.register("codes", QRCodeViewSet, basename="qrcode")

urlpatterns = [
    path("", include(router.urls)),
    path("scan/", QRScanView.as_view(), name="qr-scan"),
    path("token/redeem/", ScanTokenRedeemView.as_view(), name="token-redeem"),
    path("alerts/<uuid:alert_id>/respond/", QRAlertRespondView.as_view(), name="qr-alert-respond"),
]
