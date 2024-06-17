import os

import boto3

from config.secrets import get_secret
from config.settings.base import *

APP_ENV = "dev"
DJANGO_SECRET = get_secret(f"{PROJECT_NAME}/{APP_ENV}/django")
SECRET_KEY = DJANGO_SECRET["key"]

DEBUG = True
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = [f"https://admin.dev.{DOMAIN}"]

CORS_ALLOW_ALL_ORIGINS = True

WEBSOCKET_URL = f"https://ws.dev.{DOMAIN}"

DATABASE_SECRET = get_secret(f"{PROJECT_NAME}/{APP_ENV}/db")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DATABASE_SECRET["dbname"],
        "USER": DATABASE_SECRET["username"],
        "PASSWORD": DATABASE_SECRET["password"],
        "HOST": DATABASE_SECRET["host"],
        "PORT": DATABASE_SECRET["port"],
    },
}


# REDIS
REDIS_HOST = os.getenv("REDIS_HOST")

# CHANNELS
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, 6379)],
        },
    },
}

# CELERY
CELERY_BROKER_URL = f"sqs://"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "region": "ap-northeast-2",
    "queue_name_prefix": f"{PROJECT_NAME}-dev-",
}


# S3
AWS_REGION = "ap-northeast-2"
AWS_STORAGE_BUCKET_NAME = f"{PROJECT_NAME}-dev-bucket"
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=864000"}
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = "public-read"
AWS_S3_SECURE_URLS = True


# MEDIA
MEDIAFILES_LOCATION = "_media"
DEFAULT_FILE_STORAGE = "config.storages.MediaStorage"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIAFILES_LOCATION}/"


# STATIC
STATICFILES_LOCATION = "_static"
STATICFILES_STORAGE = "config.storages.StaticStorage"
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STATICFILES_LOCATION}/"


boto3_client = boto3.client("logs", region_name="ap-northeast-2")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "cloudwatch": {
            "format": "%(message)s",
        },
    },
    "filters": {
        "sensitive": {
            "()": "config.filters.SensitiveFilter",
        },
    },
    "handlers": {
        "watchtower_info": {
            "level": "INFO",
            "class": "watchtower.CloudWatchLogHandler",
            "boto3_client": boto3_client,
            "log_group": f"{PROJECT_NAME}/dev/info",
            "log_group_retention_days": 14,
            "stream_name": "web-{strftime:%Y-%m-%d}",
            "filters": ["sensitive"],
        },
        "watchtower_error": {
            "level": "ERROR",
            "class": "watchtower.CloudWatchLogHandler",
            "boto3_client": boto3_client,
            "log_group": f"{PROJECT_NAME}/dev/error",
            "log_group_retention_days": 30,
            "stream_name": "web-{strftime:%Y-%m-%d}",
            "filters": ["sensitive"],
        },
    },
    "loggers": {
        "request": {
            "handlers": ["watchtower_info"],
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["watchtower_error"],
            "level": "ERROR",
        },
    },
}
