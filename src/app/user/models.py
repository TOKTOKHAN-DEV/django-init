from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from app.common.models import BaseModelMixin


class UserSocialKindChoices(models.TextChoices):
    KAKAO = "kakao", "카카오"
    NAVER = "naver", "네이버"
    FACEBOOK = "facebook", "페이스북"
    GOOGLE = "google", "구글"
    APPLE = "apple", "애플"


class User(BaseModelMixin, AbstractBaseUser):
    username = models.CharField(verbose_name="유저네임", max_length=100, unique=True)
    password = models.CharField(verbose_name="비밀번호", max_length=128)
    social_kind = models.CharField(
        verbose_name="소셜",
        max_length=10,
        choices=UserSocialKindChoices,
        null=True,
        blank=True,
        editable=False,
    )
    last_login = None
    is_authenticated = True
    is_active = True
    USERNAME_FIELD = "username"

    class Meta:
        db_table = "user"
        verbose_name = "유저"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    @property
    def access_token(self):
        return AccessToken.for_user(self)

    @property
    def refresh_token(self):
        return RefreshToken.for_user(self)
