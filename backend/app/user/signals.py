from django.db.models.signals import pre_delete
from django.dispatch import receiver

from app.user.models import User
from app.withdrawal_user.models import WithdrawalUser


@receiver(pre_delete, sender=User)
def deleted_user(sender, instance, **kwargs):
    user_data = instance.__dict__
    del user_data["_state"]
    WithdrawalUser.objects.create(**user_data)
