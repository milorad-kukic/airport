from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import Aircraft
from airport.exceptions import StateConflict

STATE_FLOW = {
    Aircraft.PARKED: [Aircraft.TAKE_OFF],
    Aircraft.TAKE_OFF: [Aircraft.AIRBORNE],
    Aircraft.AIRBORNE: [Aircraft.APPROACH],
    Aircraft.APPROACH: [Aircraft.AIRBORNE, Aircraft.LANDED]
}


class AircraftSerializer(serializers.ModelSerializer):

    class Meta:
        model = Aircraft
        fields = ('id', 'call_sign', 'state', 'longitude', 'latitude',
                  'altitude', 'heading')
        read_only_fields = ('id',)
        extra_kwargs = {
            'call_sign': {
                'validators': []
            }
        }

    def is_valid(self, raise_exception=False):
        valid = super().is_valid(raise_exception)

        if valid:
            self.validate_next_state()
            self.validate_empty_runway()
            self.validate_no_other_approaching()

        return valid

    def validate_next_state(self):
        try:
            aircraft = Aircraft.objects.get(call_sign=self.data['call_sign'])

            valid_next_states = STATE_FLOW.get(aircraft.state)

            if not self.data['state'] in valid_next_states:
                raise StateConflict()
        except Aircraft.DoesNotExist:
            pass

    def validate_empty_runway(self):
        if self.data['state'] in [Aircraft.TAKE_OFF, Aircraft.LANDED]:
            on_runway = Aircraft.objects.filter(
                    state__in=[Aircraft.TAKE_OFF, Aircraft.LANDED]
            ).count()

            RUNWAY_CONT = 1
            if settings.AIRPORT_RUNAWAYS:
                RUNWAY_CONT = settings.AIRPORT_RUNAWAYS

            if on_runway > RUNWAY_CONT - 1:
                raise StateConflict()

    def validate_no_other_approaching(self):
        if self.data['state'] == Aircraft.APPROACH:
            try:
                Aircraft.objects.get(state=Aircraft.APPROACH)
                raise StateConflict()
            except Aircraft.DoesNotExist:
                pass


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = ('call_sign', 'type', 'longitude', 'latitude',
                  'altitude', 'heading')
        extra_kwargs = {
            'call_sign': {
                'validators': []
            }
        }

    def is_valid(self, raise_exception=False):
        valid = super().is_valid(raise_exception)

        if valid:
            from_db = Aircraft.objects.get(call_sign=self.data['call_sign'])
            if self.data['type'] != from_db.type:
                raise ValidationError()

        return valid
