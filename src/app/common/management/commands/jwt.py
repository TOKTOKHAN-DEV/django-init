import json

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
