from django.apps import apps
from django.db.models import FileField, ImageField

FIELD_CHOICES = []


def get_file_fields():
    global FIELD_CHOICES
    if not FIELD_CHOICES:
        for model in apps.get_models():
            for field in model._meta.fields:
                if isinstance(field, (ImageField, FileField)):
                    field_id = f"{model._meta.app_label}.{model.__name__}.{field.name}"
                    field_label = f"{field.verbose_name}"
                    FIELD_CHOICES.append((field_id, field_label))

    return FIELD_CHOICES
