import os

import boto3
import requests

from app.common.secrets import get_secret
from config.settings.base import *

APP_ENV = "prod"
DEBUG = False
SECRET_KEY = get_secret(f"{PROJECT_NAME}/{APP_ENV}/django")["key"]

API_URL = f"https://api.{DOMAIN}"
WEBSOCKET_URL = f"https://ws.{DOMAIN}"

ALLOWED_HOSTS = [f"api.{DOMAIN}", f"admin.{DOMAIN}"]
METADATA_URI = os.environ.get("ECS_CONTAINER_METADATA_URI")
if METADATA_URI:
    try:
        response = requests.get(METADATA_URI, timeout=0.1)
        data = response.json()
        ALLOWED_HOSTS.append(data["Networks"][0]["IPv4Addresses"][0])
    except Exception as e:
        print(e, "no ec2 instance")
CSRF_TRUSTED_ORIGINS = [f"https://admin.{DOMAIN}"]
CORS_ALLOWED_ORIGINS = [
    f"https://{DOMAIN}",
    f"https://www.{DOMAIN}",
]


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
    "reader": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DATABASE_SECRET["dbname"],
        "USER": DATABASE_SECRET["username"],
        "PASSWORD": DATABASE_SECRET["password"],
        "HOST": DATABASE_SECRET["host"].replace(".cluster-", ".cluster-ro-"),
        "PORT": DATABASE_SECRET["port"],
    },
}


# CELERY
CELERY_BROKER_URL = f"sqs://"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "region": "ap-northeast-2",
    "queue_name_prefix": f"{PROJECT_NAME}-prod-",
}


# S3
AWS_STORAGE_BUCKET_NAME = f"{PROJECT_NAME}-prod-bucket"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=864000"}


# STATIC
STATICFILES_LOCATION = "_static"
STATICFILES_STORAGE = "app.common.storages.StaticStorage"
STATIC_URL = f"/{STATICFILES_LOCATION}/"


# MEDIA
MEDIAFILES_LOCATION = "_media"
DEFAULT_FILE_STORAGE = "app.common.storages.PublicMediaStorage"
MEDIA_URL = f"/{MEDIAFILES_LOCATION}/"



# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
}


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
            "log_group": f"{PROJECT_NAME}/{APP_ENV}/info",
            "log_group_retention_days": 14,
            "stream_name": "web-{strftime:%Y-%m-%d}",
            "filters": ["sensitive"],
        },
        "watchtower_error": {
            "level": "ERROR",
            "class": "watchtower.CloudWatchLogHandler",
            "boto3_client": boto3_client,
            "log_group": f"{PROJECT_NAME}/{APP_ENV}/error",
            "log_group_retention_days": 30,
            "stream_name": "web-{strftime:%Y-%m-%d}",
            "filters": ["sensitive"],
        },
    },
    "loggers": {
        "request": {
            "handlers": ["watchtower_info", "watchtower_error"],
            "level": "INFO",
        },
    },
}
