from uuid import uuid4

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        abstract = True
