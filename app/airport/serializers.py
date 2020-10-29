from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import Aircraft

STATE_FLOW = {
    Aircraft.PARKED: [Aircraft.TAKE_OFF],
    Aircraft.TAKE_OFF: [Aircraft.AIRBORNE],
    Aircraft.AIRBORNE: [Aircraft.APPROACH],
    Aircraft.APPROACH: [Aircraft.AIRBORNE, Aircraft.LANDED]
}


class AircraftSerializer(serializers.ModelSerializer):

    class Meta:
        model = Aircraft
        fields = ('id', 'call_sign', 'state')
        read_only_fields = ('id',)
        extra_kwargs = {
            'call_sign': {
                'validators': []
            }
        }

    def is_valid(self, raise_exception=False):
        valid = super().is_valid(raise_exception)

        if valid:
            try:
                aircraft = Aircraft.objects.get(call_sign=self.data['call_sign'])

                valid_next_states = STATE_FLOW.get(aircraft.state)

                if not self.data['state'] in valid_next_states:
                    raise ValidationError()
            except Aircraft.DoesNotExist:
                pass

        return valid
