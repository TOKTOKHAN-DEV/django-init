from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

from app.common.models import BaseModel


class AdminUserManager(BaseUserManager):
    def create_superuser(self, username, password, **extra_fields):
        username = self.model.normalize_username(username)
        user = self.model(username=username, is_superuser=True, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class AdminUser(AbstractBaseUser):
    username = models.CharField(verbose_name="유저네임", max_length=20, unique=True)
    password = models.CharField(verbose_name="비밀번호", max_length=128)
    name = models.CharField(verbose_name="이름", max_length=20, null=True, blank=True)
    email = models.EmailField(verbose_name="이메일", null=True, blank=True)
    phone = models.CharField(verbose_name="휴대폰", max_length=11, null=True, blank=True)
    is_superuser = models.BooleanField(verbose_name="최고관리자")

    last_login = None
    is_staff = True
    USERNAME_FIELD = "username"
    objects = AdminUserManager()

    class Meta:
        db_table = "admin_user"
        verbose_name = "관리자"
        verbose_name_plural = verbose_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, module):
        return True
