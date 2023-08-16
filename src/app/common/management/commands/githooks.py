import configparser
import os
from shutil import copyfile

from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, **options):
        if options.get("delete"):
            return self.delete_hooks()
        return self.create_hooks()

    def add_arguments(self, parser):
        parser.add_argument("--delete", "-d", action="store_true")

    def create_hooks(self):
        from_dir = settings.BASE_DIR / "app" / "common" / "management" / "githooks"
        to_dir = settings.ROOT_DIR / ".git" / "hooks"
        for filename in os.listdir(from_dir):
            copyfile(from_dir / filename, to_dir / filename)
            os.chmod(to_dir / filename, 0o755)
            print(f'"{filename}" file is created.')

        # git_config = settings.ROOT_DIR / ".git" / "config"
        # config = configparser.ConfigParser()
        # config.read(git_config)
        # if "alias" not in config:
        #     config.add_section("alias")
        # config.set("alias", "cm", "commit --no-edit")
        # with open(git_config, "w") as f:
        #     config.write(f)
        #     print('"cm" alias is added.')

    def delete_hooks(self):
        from_dir = settings.BASE_DIR / "app" / "common" / "management" / "githooks"
        to_dir = settings.ROOT_DIR / ".git" / "hooks"
        for filename in os.listdir(from_dir):
            try:
                os.remove(to_dir / filename)
                print(f'"{filename}" file is deleted.')
            except FileNotFoundError:
                print(f'"{filename}" file is already deleted.')

        # git_config = settings.ROOT_DIR / ".git" / "config"
        # config = configparser.ConfigParser()
        # config.read(git_config)
        # try:
        #     config.remove_option("alias", "cm")
        #     with open(git_config, "w") as f:
        #         config.write(f)
        #         print('"cm" alias is removed.')
        # except configparser.NoSectionError:
        #     pass
