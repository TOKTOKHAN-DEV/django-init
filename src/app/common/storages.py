from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class PublicMediaStorage(S3Boto3Storage):
    location = "_media/public"
    default_acl = "public-read"
    file_overwrite = False
    querystring_auth = False


class PrivateMediaStorage(S3Boto3Storage):
    location = "_media/private"
    default_acl = "private"
    file_overwrite = False
    querystring_auth = True


class StaticStorage(S3Boto3Storage):
    location = "_static"
    file_overwrite = True
    querystring_auth = False
