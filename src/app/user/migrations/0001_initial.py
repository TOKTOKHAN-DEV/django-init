# Generated by Django 4.2.3 on 2024-08-12 14:19

import django.contrib.auth.validators
import django.core.validators
import django.utils.timezone
from django.db import migrations, models

import app.user.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="생성일시")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일시")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that username already exists."},
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="username",
                    ),
                ),
                ("email", models.EmailField(max_length=254, verbose_name="이메일")),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=11,
                        validators=[
                            django.core.validators.validate_integer,
                            django.core.validators.MinLengthValidator(10),
                        ],
                        verbose_name="휴대폰",
                    ),
                ),
                ("is_staff", models.BooleanField(default=False, verbose_name="스태프")),
                ("is_superuser", models.BooleanField(default=False, verbose_name="슈퍼유저여부")),
                ("is_active", models.BooleanField(default=True, verbose_name="활성화여부")),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="가입일")),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "유저",
                "verbose_name_plural": "유저",
                "db_table": "user",
            },
            managers=[
                ("objects", app.user.models.UserManager()),
            ],
        ),
    ]
