from uuid import uuid4

from django.conf import settings
from django.core.management import BaseCommand

xml_template = """<?xml version="1.0" encoding="UTF-8"?>
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

local_xml_template = """<?xml version="1.0" encoding="UTF-8"?>
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
        dir_path = settings.BASE_DIR.parent / ".idea"
        self.write_xml(xml_template, dir_path / "dataSources.xml", UUID=uuid, **database)
        self.write_xml(local_xml_template, dir_path / "dataSources.local.xml", UUID=uuid, **database)

    @staticmethod
    def write_xml(template, file_path, **kwargs):
        formated_xml_data = template.format(**kwargs)
        with open(file_path, "w") as f:
            f.write(formated_xml_data)
