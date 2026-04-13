from django.apps import AppConfig


class AuthIdentityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auth_identity"
    label = "auth_identity"
    verbose_name = "Auth & Identity"
