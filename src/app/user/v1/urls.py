from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.user.v1.views import UserViewSet, kakao_authorize, kakao_token

router = DefaultRouter()
router.register("user", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/kakao/authorize/", kakao_authorize, name="kakao-authorize"),
    path("auth/kakao/token/", kakao_token, name="kakao-token"),
]
