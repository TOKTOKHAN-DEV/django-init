from django.urls import include, path

urlpatterns = [
    path("", include("api.v1.user.urls")),
    path("", include("api.v1.presigned_url.urls")),
    path("", include("api.v1.verifier.urls")),
    path("", include("api.v1.chat.urls")),
]
