from .base import *  # noqa

DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True
BYPASS_OTP_VERIFICATION = True
BYPASS_CNIC_VERIFICATION = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "DEBUG"},
}
