import random

from django.apps import apps
from django.db.models import ForeignKey
from django_seed import Seed


def get_seed_data(app_name, model_name, number):
    seeder = Seed.seeder()
    model = apps.get_model(app_label=app_name, model_name=model_name)
    fk_list = [(field.name, field.related_model) for field in model._meta.get_fields() if isinstance(field, ForeignKey)]
    fk = {i[0]: random.choice(i[1].objects.all()) for i in fk_list}

    seeder.add_entity(model, number, fk)
    seeder.execute()
