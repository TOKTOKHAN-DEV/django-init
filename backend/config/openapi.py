from django.conf import settings
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers


class CustomAutoSchema(AutoSchema):
    def _get_response_bodies(self, direction="response"):
        response_bodies = super()._get_response_bodies(direction)
        if self.method in ["POST", "PUT", "PATCH"]:
            serializer = self.get_request_serializer()
            component = self.resolve_serializer(serializer, direction)
            field_list = [settings.REST_FRAMEWORK["NON_FIELD_ERRORS_KEY"]]
            for name, field in serializer.get_fields().items():
                if not field.read_only:
                    field_list.append(name)
            response_bodies[400] = self._get_response_for_code(
                inline_serializer(
                    name=f"{component.name}ValidationError",
                    fields={
                        field: serializers.ListField(required=False, child=serializers.CharField())
                        for field in field_list
                    },
                ),
                400,
            )
        return response_bodies

    def _map_serializer_field(self, field, direction, bypass_extensions=False):
        map_serializer_field = super()._map_serializer_field(field, direction, bypass_extensions)
        if isinstance(field, serializers.MultipleChoiceField) or isinstance(field, serializers.ChoiceField):
            map_serializer_field.update({"x-enumNames": field.choices.values()})
        return map_serializer_field
