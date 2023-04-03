from django.urls import include, path

urlpatterns = [
    path("", include("app.user.v1.urls")),
    path("", include("app.presigned_url.v1.urls")),
    path("", include("app.verifier.v1.urls")),
    path("", include("app.chat.v1.urls")),
]
