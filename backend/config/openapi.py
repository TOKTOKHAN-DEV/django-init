from django.conf import settings
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import is_basic_serializer
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers


class CustomAutoSchema(AutoSchema):
    def _get_response_bodies(self, direction="response"):
        response_bodies = super()._get_response_bodies(direction)
        if self.method in ["POST", "PUT", "PATCH"]:
            serializer = self.get_request_serializer()
            if serializer and is_basic_serializer(serializer):
                component = self.resolve_serializer(serializer, direction)
                response_bodies[400] = self._get_response_for_code(
                    inline_serializer(
                        name=f"{component.name}ValidationError",
                        fields={
                            settings.REST_FRAMEWORK["NON_FIELD_ERRORS_KEY"]: serializers.ListField(
                                required=False, child=serializers.CharField()
                            ),
                            **self._get_fields(serializer),
                        },
                    ),
                    400,
                )
        return response_bodies

    def _get_fields(self, serializer):
        fields = {}
        for name, field in serializer.get_fields().items():
            if field.read_only:
                continue
            if issubclass(field.__class__, serializers.Serializer):
                component = self.resolve_serializer(field, "response")
                fields[name] = inline_serializer(
                    required=False,
                    name=f"{component.name}ValidationError",
                    fields=self._get_fields(field),
                )
            else:
                fields[name] = serializers.ListField(required=False, child=serializers.CharField())
        return fields

    def _map_serializer_field(self, field, direction, bypass_extensions=False):
        map_serializer_field = super()._map_serializer_field(field, direction, bypass_extensions)
        if isinstance(field, serializers.MultipleChoiceField) or isinstance(field, serializers.ChoiceField):
            if not direction:
                map_serializer_field.update({"x-enumNames": [field.choices.get(key) for key in sorted(field.choices)]})
            else:
                map_serializer_field.update({"x-enumNames": [field.choices.get(key) for key in field.choices]})
        return map_serializer_field
