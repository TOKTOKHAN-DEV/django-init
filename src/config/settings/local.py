import datetime
import os

import boto3

from app.common.secrets import get_secret
from config.settings.base import *

APP_ENV = "dev"
DEBUG = True
SECRET_KEY = "pj%2ze09(g)i^joilp-f8gvs)6ou_m036u3ejs^ky&9nse5k92"

API_URL = f"https://api.dev.{DOMAIN}"
WEBSOCKET_URL = f"https://ws.dev.{DOMAIN}"

ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True

# local database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# remote database
# DATABASE_SECRET = get_secret(f'{PROJECT_NAME}/{APP_ENV}/db')
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': DATABASE_SECRET['dbname'],
#         'USER': DATABASE_SECRET['username'],
#         'PASSWORD': DATABASE_SECRET['password'],
#         'HOST': DATABASE_SECRET['host'],
#         'PORT': DATABASE_SECRET['port'],
#     },
#     'reader': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': DATABASE_SECRET['dbname'],
#         'USER': DATABASE_SECRET['username'],
#         'PASSWORD': DATABASE_SECRET['password'],
#         'HOST': DATABASE_SECRET['host'].replace('.cluster-', '.cluster-ro-'),
#         'PORT': DATABASE_SECRET['port'],
#     },
# }


# CELERY
CELERY_BROKER_URL = f"sqs://"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "region": "ap-northeast-2",
    "queue_name_prefix": f"{PROJECT_NAME}-{APP_ENV}-",
}


# S3
AWS_STORAGE_BUCKET_NAME = f"{PROJECT_NAME}-{APP_ENV}-bucket"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=864000"}


# MEDIA
MEDIAFILES_LOCATION = "_media"
MEDIA_ROOT = BASE_DIR / MEDIAFILES_LOCATION
MEDIA_URL = f"/{MEDIAFILES_LOCATION}/"


# STATIC
STATIC_ROOT = BASE_DIR / "_static"
STATIC_URL = "/_static/"


# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=365),
    "ROTATE_REFRESH_TOKENS": True,
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple_formatter": {
            "format": "{message}",
            "style": "{",
        },
    },
    "handlers": {
        "simple_console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple_formatter",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["simple_console"],
            "level": "DEBUG",
        },
    },
}
