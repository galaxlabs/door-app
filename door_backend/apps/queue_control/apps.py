from django.apps import AppConfig


class QueueControlConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.queue_control"
    label = "queue_control"
    verbose_name = "Queue Control"
