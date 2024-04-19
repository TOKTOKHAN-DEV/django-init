import json
import subprocess

from django.core.management import BaseCommand, CommandError
from rest_framework_simplejwt.tokens import RefreshToken

from app.user.models import User


class Command(BaseCommand):
    help = "유저의 JWT를 가져옵니다. (settings 설정에 주의하세요.)"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int, help="User ID")

    def handle(self, *args, **options):
        user_id = options.get("user_id")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as e:
            raise CommandError(e)
        refresh = RefreshToken.for_user(user)
        response = {"access_token": str(refresh.access_token), "refresh_token": str(refresh)}
        print("\033[32m" + json.dumps(response) + "\033[0m")
        self.set_clipboard_text(response["access_token"])

    @staticmethod
    def set_clipboard_text(text):
        process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        process.communicate(text.encode("utf-8"))
        print("\033[35m" + "access token이 클립보드에 복사되었습니다." + "\033[0m")
