from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import include, path
from django.utils.safestring import mark_safe

urlpatterns = [
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("", admin.site.urls),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = (
    mark_safe(f'<img src="{settings.STATIC_URL + settings.SITE_LOGO}" height="28" style="vertical-align: bottom;" />')
    if settings.SITE_LOGO
    else f"{settings.SITE_NAME} 어드민"
)
admin.site.site_url = settings.FRONTEND_URL
admin.site.unregister(Group)
