from django.core.management.base import BaseCommand

from app.common.utils import get_seed_data


class Command(BaseCommand):
    help = f"이 명령은 입력 받은 모델의 더미 데이터를 만듭니다. ex) app_name.model_name"

    def add_arguments(self, parser):
        parser.add_argument("model", type=str, help=f"모델을 입력하세요")
        parser.add_argument("--number", "-n", default=10, type=int, help=f"몇개의 데이터를 생성 하시겠습니까?")

    def handle(self, *args, **options):
        app_name, model_name = options["model"].split(".")
        number = options.get("number")

        get_seed_data(app_name, model_name, number)
        self.stdout.write(self.style.SUCCESS(f"{number} {model_name} 생성!"))
