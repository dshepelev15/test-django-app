from django.contrib.auth.models import User
from django.db import models

from .base_model import BaseModel


class Account(BaseModel):
    owner = models.OneToOneField(User, on_delete=models.PROTECT)
    balance = models.DecimalField(default=0, decimal_places=2, max_digits=12)
