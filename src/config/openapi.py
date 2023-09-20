from django.conf import settings
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import is_basic_serializer
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers


class CommonErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()


class CustomAutoSchema(AutoSchema):
    def _get_response_bodies(self, direction="response"):
        response_bodies = super()._get_response_bodies(direction)
        # filter_parameters = self._get_filter_parameters()
        # if filter_parameters:
        #     required_fields = []
        #     for filter_parameter in filter_parameters:
        #         if filter_parameter["required"]:
        #             required_fields.append(filter_parameter["name"])
        #     if required_fields:
        #         name = self.view.filterset_class.__name__
        #         response_bodies[400] = self._get_response_for_code(
        #             inline_serializer(
        #                 name=f"{name}Error",
        #                 fields={
        #                     "message": inline_serializer(
        #                         name=f"{name}ErrorMessage",
        #                         fields={
        #                             field: serializers.ListField(required=False, child=serializers.CharField())
        #                             for field in required_fields
        #                         },
        #                     ),
        #                     "error_code": serializers.CharField(),
        #                 },
        #             ),
        #             "400",
        #         )

        if self.method in ["POST", "PUT", "PATCH"]:
            self._get_400_error(direction, response_bodies)
        response_bodies[401] = self._get_common_error("401")
        response_bodies[403] = self._get_common_error("403")
        if self.view.detail:
            response_bodies[404] = self._get_common_error("404")
        return response_bodies

    def _get_400_error(self, direction, response_bodies):
        serializer = self.get_request_serializer()
        if serializer and is_basic_serializer(serializer):
            component = self.resolve_serializer(serializer, direction)
            response_bodies[400] = self._get_response_for_code(
                inline_serializer(
                    name=f"{component.name}Error",
                    fields={
                        "message": inline_serializer(
                            name=f"{component.name}ErrorMessage",
                            fields={
                                settings.REST_FRAMEWORK["NON_FIELD_ERRORS_KEY"]: serializers.ListField(
                                    required=False, child=serializers.CharField()
                                ),
                                **self._get_fields(serializer),
                            },
                        ),
                        "error_code": serializers.CharField(),
                    },
                ),
                400,
            )

    def _get_common_error(self, status_code):
        return self._get_response_for_code(
            CommonErrorSerializer(),
            status_code,
        )

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
            map_serializer_field.update({"x-enumNames": [field.choices.get(key) for key in field.choices]})
        return map_serializer_field
