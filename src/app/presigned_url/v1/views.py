from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from app.presigned_url.v1.serializers import PresignedSerializer


@extend_schema(
    summary="미리 서명된 URL 발급",
    description=f"""
![file_upload_flow]({settings.STATIC_URL}docs/file_upload_flow.png)
* 플로우 1, 2를 input onChange 핸들러에서 실행해야합니다.
1. 미시 서명된 URL 발급
2. 미리 서명된 URL로 파일 업로드
    - Method: `POST`
    - Url: `URL` (1에서 발급받은 URL)
    - form-data: `FIELDS` (1에서 응답받은 fields 안의 Value들)
    - Headers: `Content-Type: file.type` (input의 file.type)
""",
)
class PresignedUrlCreateView(CreateAPIView):
    serializer_class = PresignedSerializer
    permission_classes = [IsAuthenticated]
