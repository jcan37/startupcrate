from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.CharField(max_length=256)
    personal = models.BooleanField(default=False)

    def __str__(self):
        return str(self.value)
