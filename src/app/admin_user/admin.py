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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["password"].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            instance.password = make_password(password)
        if commit:
            instance.save()
        return instance


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    form = AdminUserAdminForm
    list_display = ["id", "username", "name", "email", "phone"]
