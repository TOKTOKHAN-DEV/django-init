from rest_framework import status
from rest_framework.exceptions import APIException


class SocialAccountNotFoundError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail):
        self.detail = {"social_token": detail}
