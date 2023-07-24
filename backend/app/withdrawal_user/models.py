from app.common.models import BaseModel
from app.user.models import BaseUser


class WithdrawalUser(BaseUser):
    class Meta:
        db_table = "withdrawal_user"
        verbose_name = "탈퇴한 유저"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
