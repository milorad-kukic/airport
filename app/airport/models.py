from django.db import models


class Aircraft(models.Model):
    PARKED = 'PARKED'
    TAKE_OFF = 'TAKE_OFF'
    AIRBORNE = 'AIRBORNE'
    APPROACH = 'APPROACH'
    LANDED = 'LANDED'

    STATE_FLOW = {
        PARKED: [TAKE_OFF],
        TAKE_OFF: [AIRBORNE],
        AIRBORNE: [APPROACH],
        APPROACH: [LANDED]
    }

    STATUSES = [
        (PARKED, 'Parked'),
        (TAKE_OFF, 'Take-off'),
        (AIRBORNE, 'Airborne'),
        (APPROACH, 'Approach'),
        (LANDED, 'Landed'),
    ]

    call_sign = models.CharField(max_length=50, unique=True)
    state = models.CharField(
            max_length=50,
            choices=STATUSES,
            null=False, blank=False,
            default='PARKED')

    def __str__(self):
        return self.call_sign

    def valid_next_state(self):
        if self.state in Aircraft.STATE_FLOW.keys():
            return Aircraft.STATE_FLOW[self.state]
