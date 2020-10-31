from django.db import models
from django.utils import timezone


class Aircraft(models.Model):
    PARKED = 'PARKED'
    TAKE_OFF = 'TAKE_OFF'
    AIRBORNE = 'AIRBORNE'
    APPROACH = 'APPROACH'
    LANDED = 'LANDED'

    STATUSES = [
        (PARKED, 'Parked'),
        (TAKE_OFF, 'Take-off'),
        (AIRBORNE, 'Airborne'),
        (APPROACH, 'Approach'),
        (LANDED, 'Landed'),
    ]

    AIRCRAFT_TYPES = [
        ('AIRLINER', 'Airliner'),
        ('PRIVATE', 'Private'),
    ]

    call_sign = models.CharField(max_length=50, unique=True)
    type = models.CharField(
            max_length=50,
            null=False,
            blank=False,
            choices=AIRCRAFT_TYPES,
            default='PRIVATE'
    )
    state = models.CharField(
            max_length=50,
            choices=STATUSES,
            null=False, blank=False,
            default='PARKED')

    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    altitude = models.IntegerField(default=0)
    heading = models.IntegerField(default=0)

    def __str__(self):
        return self.call_sign


class StateChangeLog(models.Model):
    OUTCOMES = [
        ('ACCEPTED', 'ACCEPTED'),
        ('REJECTED', 'REJECTED')
    ]
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    from_state = models.CharField(max_length=50, choices=Aircraft.STATUSES)
    to_state = models.CharField(max_length=50, choices=Aircraft.STATUSES)
    outcome = models.CharField(max_length=10, choices=OUTCOMES)
    description = models.CharField(max_length=255)
    time = models.DateTimeField(default=timezone.now)
