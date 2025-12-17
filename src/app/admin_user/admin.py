from django import forms
from django.contrib import admin
from django.contrib.auth.hashers import make_password

from app.admin_user.models import AdminUser


class AdminUserAdminForm(forms.ModelForm):
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(attrs={"class": "vTextField"}),
        required=False,
        help_text="변경시에만 입력하세요.",
    )

    class Meta:
        model = AdminUser
        fields = "__all__"
        exclude = ["password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["password"].required = True

    def save(self, commit=True):
        password = self.cleaned_data.pop("password", None)
        instance = super().save(commit=False)
        if password:
            instance.set_password(password)
        if commit:
            instance.save()
        return instance


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    form = AdminUserAdminForm
    list_display = ["id", "username", "name", "email", "phone", "is_superuser"]
    search_fields = ["username", "name", "email", "phone"]
    search_help_text = "유저네임, 이름, 이메일, 휴대폰번호로 검색하세요."
    fields = [
        "username",
        "password",
        "name",
        "email",
        "phone",
        "is_superuser",
    ]

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user == obj

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser and request.user != obj
