import mimetypes

from storages.backends.s3boto3 import S3Boto3Storage


class DefaultMediaStorage(S3Boto3Storage):
    location = ""

    def generate_presigned_post(self, object_key):
        object_key = self.get_available_name(f"{self.location}/{object_key}")

        content_type, _ = mimetypes.guess_type(object_key)
        if content_type is None:
            content_type = "application/octet-stream"  # 기본값
        fields = {
            "Content-Type": content_type,
        }
        conditions = [
            {"Content-Type": content_type},
            ["content-length-range", 0, 20971520],
        ]  # 20MB  # 지정한 값과 같아야만 허용

        response = self.bucket.meta.client.generate_presigned_post(
            self.bucket.name,
            object_key,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=360,
        )
        return response


class StaticStorage(S3Boto3Storage):
    location = "_static"
    default_acl = "public-read"
    file_overwrite = True
    querystring_auth = False


class PublicMediaStorage(DefaultMediaStorage):
    location = "_media/public"
    default_acl = "public-read"
    file_overwrite = False
    querystring_auth = False


class PrivateMediaStorage(DefaultMediaStorage):
    location = "_media/private"
    default_acl = "private"
    file_overwrite = False
    querystring_auth = True
