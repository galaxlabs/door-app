from django.contrib import admin
from .models import User, OTP, UserDevice, EmailVerification, UserSession


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "phone_number", "full_name", "role", "status", "is_email_verified", "is_phone_verified", "created_at_server"]
    search_fields = ["email", "phone_number", "full_name"]
    list_filter = ["role", "status", "is_email_verified", "is_phone_verified", "is_active"]
    actions = ["mark_email_verified", "mark_phone_verified"]

    @admin.action(description="Mark selected users as email verified")
    def mark_email_verified(self, request, queryset):
        queryset.update(is_email_verified=True)

    @admin.action(description="Mark selected users as phone verified")
    def mark_phone_verified(self, request, queryset):
        queryset.update(is_phone_verified=True)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ["phone", "used", "expires_at", "created_at_server"]


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ["user", "platform", "device_id", "last_seen"]


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ["email", "user", "status", "expires_at", "verified_at"]
    search_fields = ["email", "user__email", "user__phone_number"]
    list_filter = ["status"]


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "issued_at", "expires_at", "last_rotated_at"]
    search_fields = ["user__email", "user__phone_number", "refresh_jti"]
    list_filter = ["status"]
