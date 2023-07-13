from functools import update_wrapper

from django.contrib.admin import AdminSite as DjangoAdminSite
from django.http import JsonResponse
from django.urls import path


class AdminSite(DjangoAdminSite):
    def get_urls(self):
        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        urls = [
            path("example/", wrap(self.example_view), name="example"),
        ]
        urls += super().get_urls()
        return urls

    def example_view(self, request, *args, **kwargs):
        return JsonResponse(data={})
