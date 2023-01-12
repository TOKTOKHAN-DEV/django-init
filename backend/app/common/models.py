from django.db import models
from safedelete import SOFT_DELETE
from safedelete.models import SafeDeleteModel


class BaseModelMixin(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    created = models.DateTimeField(verbose_name="생성일시", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="수정일시", auto_now=True)

    class Meta:
        abstract = True


BaseModel = BaseModelMixin
