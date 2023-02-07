from django.urls import path

from api.v1.presigned_url.views import PresignedUrlCreateView

urlpatterns = [
    path("presigned_url/", PresignedUrlCreateView.as_view()),
]
