"""
Django base settings for Door App backend.
"""
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
BYPASS_OTP_VERIFICATION = env.bool("BYPASS_OTP_VERIFICATION", default=False)
BYPASS_CNIC_VERIFICATION = env.bool("BYPASS_CNIC_VERIFICATION", default=False)

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "channels",
    "django_filters",
    "django_celery_beat",
    "django_celery_results",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.auth_identity",
    "apps.organizations",
    "apps.qr_engine",
    "apps.queue_control",
    "apps.chat",
    "apps.broadcast",
    "apps.sync",
    "apps.audit",
    "apps.notifications",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = "auth_identity.User"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "common.middleware.AuditMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
        "ATOMIC_REQUESTS": True,
    }
}

# ---------------------------------------------------------------------------
# Cache / Redis / Channels
# ---------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_EXTENDED = True
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

# Queue routing by domain
CELERY_TASK_ROUTES = {
    "auth_identity.*": {"queue": "auth"},
    "qr_engine.*": {"queue": "qr"},
    "queue_control.*": {"queue": "queue"},
    "chat.*": {"queue": "chat"},
    "broadcast.*": {"queue": "broadcast"},
    "sync.*": {"queue": "sync"},
    "audit.*": {"queue": "audit"},
    "notifications.*": {"queue": "notifications"},
}

# Periodic jobs (via django-celery-beat)
CELERY_BEAT_SCHEDULE = {
    "expire-pending-otps-every-5-min": {
        "task": "auth_identity.expire_pending_otps",
        "schedule": 300.0,
    },
    "revoke-expired-sessions-hourly": {
        "task": "auth_identity.revoke_expired_sessions",
        "schedule": 3600.0,
    },
    "deactivate-expired-qr-codes-every-10-min": {
        "task": "qr_engine.deactivate_expired_qr_codes",
        "schedule": 600.0,
    },
    "expire-scan-tokens-every-5-min": {
        "task": "qr_engine.expire_scan_tokens",
        "schedule": 300.0,
    },
    "auto-end-stale-sessions-every-2-min": {
        "task": "queue_control.auto_end_sessions_for_closed_queues",
        "schedule": 120.0,
    },
    "dispatch-scheduled-broadcasts-every-minute": {
        "task": "broadcast.send_scheduled_messages",
        "schedule": 60.0,
    },
    "process-sync-pending-every-15-sec": {
        "task": "sync.process_pending_queue",
        "schedule": 15.0,
    },
    "dispatch-device-outbox-every-20-sec": {
        "task": "sync.dispatch_device_outbox",
        "schedule": 20.0,
    },
    "archive-expired-notifications-every-hour": {
        "task": "notifications.archive_expired",
        "schedule": 3600.0,
    },
    "prune-old-audit-logs-daily": {
        "task": "audit.prune_old_logs",
        "schedule": 86400.0,
    },
}

# ---------------------------------------------------------------------------
# Auth / JWT
# ---------------------------------------------------------------------------
from datetime import timedelta  # noqa: E402

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ---------------------------------------------------------------------------
# DRF
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "common.exceptions.door_exception_handler",
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

from django.utils.translation import gettext_lazy as _  # noqa

LANGUAGES = [
    ("en", _("English")),
    ("ar", _("Arabic")),
    ("ur", _("Urdu")),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

# ---------------------------------------------------------------------------
# Static / Media
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# OpenAPI
# ---------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "Door App API",
    "DESCRIPTION": "Offline-first QR interaction, queue, communication, and coordination platform.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
