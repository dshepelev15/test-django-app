from django.db import models

from .account import Account
from .base_model import BaseModel


class BaseOperation(BaseModel):
    account_to = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="%(class)s_operations_to"
    )
    value = models.DecimalField(decimal_places=2, max_digits=12)

    class Meta:
        abstract = True


class TopUpOperation(BaseOperation):
    pass


class TransferOperation(BaseOperation):
    account_from = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="operations_from"
    )
