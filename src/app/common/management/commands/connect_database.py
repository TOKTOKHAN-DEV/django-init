import subprocess
from uuid import uuid4

from django.conf import settings
from django.core.management import BaseCommand

xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="DataSourceManagerImpl" format="xml" multifile-model="true">
    <data-source source="LOCAL" name="{NAME}@{HOST}" uuid="{UUID}">
      <driver-ref>postgresql</driver-ref>
      <synchronize>true</synchronize>
      <jdbc-driver>org.postgresql.Driver</jdbc-driver>
      <jdbc-url>jdbc:postgresql://{HOST}:{PORT}/{NAME}?password={PASSWORD}</jdbc-url>
      <working-dir>$ProjectFileDir$</working-dir>
    </data-source>
  </component>
</project>
"""

local_xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="dataSourceStorageLocal" created-in="">
    <data-source name="{NAME}@{HOST}" uuid="{UUID}">
      <database-info product="" version="" jdbc-version="" driver-name="" driver-version="" dbms="POSTGRES" />
      <secret-storage>master_key</secret-storage>
      <user-name>{USER}</user-name>
      <schema-mapping />
    </data-source>
  </component>
</project>
"""


class Command(BaseCommand):
    help = "파이참에 데이터베이스를 연결합니다."

    def handle(self, *args, **options):
        uuid = uuid4()
        database = settings.DATABASES["default"]
        formated_xml_data = xml_data.format(
            NAME=database["NAME"],
            USER=database["USER"],
            PASSWORD=database["PASSWORD"],
            HOST=database["HOST"],
            PORT=database["PORT"],
            UUID=uuid,
        )
        file_path = settings.BASE_DIR.parent / ".idea" / "dataSources.xml"
        with open(file_path, "w") as f:
            f.write(formated_xml_data)

        formated_local_xml_data = local_xml_data.format(
            NAME=database["NAME"],
            USER=database["USER"],
            HOST=database["HOST"],
            PORT=database["PORT"],
            UUID=uuid,
        )
        file_path = settings.BASE_DIR.parent / ".idea" / "dataSources.local.xml"
        with open(file_path, "w") as f:
            f.write(formated_local_xml_data)

        self.set_clipboard_text(database["PASSWORD"])

    @staticmethod
    def set_clipboard_text(text):
        process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        process.communicate(text.encode("utf-8"))
        print("\033[35m" + "password가 클립보드에 복사되었습니다." + "\033[0m")
