from django.contrib import admin
from .models import User, OTP, UserDevice


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["phone", "full_name", "role", "is_verified", "created_at_server"]
    search_fields = ["phone", "full_name", "email"]
    list_filter = ["role", "is_phone_verified", "is_active"]


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ["phone", "used", "expires_at", "created_at_server"]


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ["user", "platform", "device_id", "last_seen"]
