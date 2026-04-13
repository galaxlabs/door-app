from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InteractionTemplateViewSet,
    TemplateFieldViewSet,
    TemplateWorkflowStateViewSet,
    TemplateActionViewSet,
    NotificationRuleViewSet,
    InteractionRecordViewSet,
    QRCodeViewSet,
    QRScanView,
    ScanTokenRedeemView,
    QRAlertRespondView,
    TemplatePackCatalogView,
    TemplatePackSeedView,
    TemplatePackAdminSetupView,
)

router = DefaultRouter()
router.register("templates", InteractionTemplateViewSet, basename="interaction-template")
router.register("template-fields", TemplateFieldViewSet, basename="template-field")
router.register("template-workflow-states", TemplateWorkflowStateViewSet, basename="template-workflow-state")
router.register("template-actions", TemplateActionViewSet, basename="template-action")
router.register("notification-rules", NotificationRuleViewSet, basename="notification-rule")
router.register("codes", QRCodeViewSet, basename="qrcode")
router.register("interactions", InteractionRecordViewSet, basename="interaction-record")

urlpatterns = [
    path("", include(router.urls)),
    path("template-packs/", TemplatePackCatalogView.as_view(), name="template-pack-catalog"),
    path("template-packs/seed/", TemplatePackSeedView.as_view(), name="template-pack-seed"),
    path("template-packs/admin-setup/", TemplatePackAdminSetupView.as_view(), name="template-pack-admin-setup"),
    path("scan/", QRScanView.as_view(), name="qr-scan"),
    path("token/redeem/", ScanTokenRedeemView.as_view(), name="token-redeem"),
    path("alerts/<uuid:alert_id>/respond/", QRAlertRespondView.as_view(), name="qr-alert-respond"),
]
