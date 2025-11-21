from django import forms
from django.contrib import admin

from app.user.models import User


class UserAdminForm(forms.ModelForm):
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(attrs={"class": "vTextField"}),
        required=False,
        help_text="변경시에만 입력하세요.",
    )

    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["password"].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            instance.set_password(password)
        if commit:
            instance.save()
        return instance


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = ["id", "username"]
    search_fields = ["username"]
    search_help_text = "유저네임으로 검색하세요."
