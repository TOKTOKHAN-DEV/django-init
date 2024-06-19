import os

import boto3
import dotenv
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from config.secrets import get_secret
from config.settings.base import *

dotenv.load_dotenv()

APP_ENV = "dev"
DEBUG = True

ALLOWED_HOSTS += ["*"]

CORS_ALLOW_ALL_ORIGINS = True

API_URL = f"https://api.dev.{DOMAIN}"
WEBSOCKET_URL = f"https://ws.dev.{DOMAIN}"

# local database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# remote database
# DATABASE_SECRET = get_secret(f'{PROJECT_NAME}/dev/db')
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


# S3
AWS_REGION = "ap-northeast-2"
AWS_STORAGE_BUCKET_NAME = f"{PROJECT_NAME}-prod-bucket"
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=864000"}
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = "public-read"
AWS_S3_SECURE_URLS = True


# REDIS
REDIS_HOST = "localhost"

# CHANNELS
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# CELERY
CELERY_BROKER_URL = f"sqs://"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "region": "ap-northeast-2",
    "queue_name_prefix": f"{PROJECT_NAME}-dev-",
}


# MEDIA
MEDIA_ROOT = BASE_DIR / "_media"
MEDIA_URL = "/_media/"


# STATIC
STATIC_ROOT = BASE_DIR / "_static"
STATIC_URL = "/_static/"

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
