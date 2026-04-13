from django.contrib import admin

from .models import (
    InteractionRecord,
    InteractionTemplate,
    NotificationRule,
    QRCode,
    TemplateAction,
    TemplateField,
    TemplateWorkflowState,
)


@admin.register(InteractionTemplate)
class InteractionTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "version", "supports_offline", "is_public")
    search_fields = ("name", "category")


@admin.register(TemplateField)
class TemplateFieldAdmin(admin.ModelAdmin):
    list_display = ("template", "field_key", "field_type", "is_required")
    list_filter = ("field_type", "is_required")


@admin.register(TemplateWorkflowState)
class TemplateWorkflowStateAdmin(admin.ModelAdmin):
    list_display = ("template", "state_name", "state_type", "order", "is_initial", "is_final")
    list_filter = ("is_initial", "is_final")


@admin.register(TemplateAction)
class TemplateActionAdmin(admin.ModelAdmin):
    list_display = ("template", "action_name", "action_key", "role_required")
    search_fields = ("action_name", "action_key")


@admin.register(NotificationRule)
class NotificationRuleAdmin(admin.ModelAdmin):
    list_display = ("template", "trigger_event", "audience_type", "channel", "priority")
    list_filter = ("audience_type", "channel", "priority")


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ("label", "template", "purpose", "owner_type", "status", "is_active")
    search_fields = ("label", "qr_token", "purpose")
    list_filter = ("status", "is_active", "owner_type")


@admin.register(InteractionRecord)
class InteractionRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "template", "qr_entity", "initiated_by", "status", "current_state")
    list_filter = ("status", "template")
