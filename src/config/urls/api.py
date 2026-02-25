from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularRedocView, SpectacularSwaggerView

from app.common.schedule_registry import autodiscover, registry

autodiscover()

api_urlpatterns = [
    path("", include("app.urls.api")),
    path("_health/", lambda request: HttpResponse()),
    path("admin/", admin.site.urls),
]


urlpatterns = [
    *api_urlpatterns,
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("openapi.json/", SpectacularJSONAPIView.as_view(patterns=api_urlpatterns), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(), name="redoc"),
]

urlpatterns += [path(f"schedule/{entry.path}", entry.view_class.as_view()) for entry in registry.all().values()]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
