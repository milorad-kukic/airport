from django.db import models


class Aircraft(models.Model):
    call_sign = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.call_sign
