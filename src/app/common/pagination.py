from collections import OrderedDict
from urllib import parse

from django.utils.encoding import force_str
from rest_framework import pagination
from rest_framework.response import Response


class LimitOffsetPagination(pagination.LimitOffsetPagination):
    default_limit = 20
    max_limit = 100

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.count),
                    ("results", data),
                ]
            )
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                },
                "is_next": {
                    "type": "boolean",
                },
                "results": schema,
            },
        }


class CursorPagination(pagination.CursorPagination):
    page_size = 20
    page_size_query_param = "page_size"
    ordering = None

    def get_ordering(self, request, queryset, view):
        ordering = super().get_ordering(request, queryset, view)
        return ordering + ("pk",)

    def encode_cursor(self, cursor):
        url = super().encode_cursor(cursor)
        query = parse.urlsplit(force_str(url)).query
        query_dict = dict(parse.parse_qsl(query, keep_blank_values=True))

        return query_dict.get(self.cursor_query_param)

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("cursor", self.get_next_link()),
                    ("results", data),
                ]
            )
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "cursor": {
                    "type": "string",
                    "nullable": True,
                },
                "results": schema,
            },
        }
