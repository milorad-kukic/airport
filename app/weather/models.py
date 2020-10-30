from django.db import models
from django.utils import timezone


class WeatherData(models.Model):
    description = models.CharField(max_length=255)
    temperature = models.DecimalField(max_digits=4, decimal_places=2)
    visibility = models.IntegerField()
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2)
    wind_deg = models.IntegerField() 
    last_update = models.DateTimeField(default=timezone.now)
