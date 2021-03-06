from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import Aircraft, StateChangeLog
from airport.exceptions import StateConflict

STATE_FLOW = {
    Aircraft.PARKED: [Aircraft.TAKE_OFF],
    Aircraft.TAKE_OFF: [Aircraft.AIRBORNE],
    Aircraft.AIRBORNE: [Aircraft.APPROACH],
    Aircraft.APPROACH: [Aircraft.AIRBORNE, Aircraft.LANDED]
}


def get_setting(key, default):
    """
    Utility method to easier access settings attributes and return
    default value if key not found in settings.

    key needs to be sent as a string. For example:
    get_setting('AIRPORT_LARGE_PARKING_SPOTS', 10)
    """

    return getattr(settings, key, default)


class AircraftSerializer(serializers.ModelSerializer):

    type = serializers.CharField(allow_null=True)

    class Meta:
        model = Aircraft
        fields = ('id', 'call_sign', 'state', 'type', 'longitude', 'latitude',
                  'altitude', 'heading')
        read_only_fields = ('id',)
        optional_fields = ['type']
        extra_kwargs = {
            'call_sign': {
                'validators': []
            },
            'type': {
                'validators': []
            }
        }

    def is_valid(self, raise_exception=False):
        valid = super().is_valid(raise_exception)

        if valid:
            try:
                self.db_object = Aircraft.objects.get(call_sign=self.data['call_sign'])
            except Aircraft.DoesNotExist:
                self.db_object = None

            self.check_mandatory_type_for_new_aircraft()
            self.validate_next_state()
            self.validate_empty_runway()
            self.validate_no_other_approaching()
            self.validate_parking_available()

        return valid

    def check_mandatory_type_for_new_aircraft(self):
        new_aircraft = self.db_object is None

        if new_aircraft and not self.data['type']:
            raise ValidationError()

    def validate_next_state(self):
        if self.db_object:
            aircraft = self.db_object

            valid_next_states = STATE_FLOW.get(aircraft.state)

            if not self.data['state'] in valid_next_states:
                raise StateConflict(
                    aircraft=aircraft,
                    from_state=aircraft.state,
                    to_state=self.data['state'],
                    description='Not a valid state change'
                )

    def validate_empty_runway(self):
        if self.data['state'] in [Aircraft.TAKE_OFF, Aircraft.LANDED]:
            on_runway = Aircraft.objects.filter(
                    state__in=[Aircraft.TAKE_OFF, Aircraft.LANDED]
            ).count()

            RUNWAY_CONT = get_setting('AIRPORT_RUNAWAYS', 1)

            if on_runway > RUNWAY_CONT - 1:
                from_state = ''
                if self.db_object:
                    from_state = self.db_object.state
                raise StateConflict(
                    aircraft=self.db_object,
                    from_state=from_state,
                    to_state=self.data['state'],
                    description='The runway is occupied'
                )

    def validate_no_other_approaching(self):
        if self.data['state'] == Aircraft.APPROACH:
            try:
                Aircraft.objects.get(state=Aircraft.APPROACH)
                from_state = ''
                if self.db_object:
                    from_state = self.db_object.state
                raise StateConflict(
                    aircraft=self.db_object,
                    from_state=from_state,
                    to_state=self.data['state'],
                    description="Other aircraft is on approach"
                )
            except Aircraft.DoesNotExist:
                pass

    def validate_parking_available(self):
        if self.db_object is None:
            type_to_check = self.data['type']
        else:
            type_to_check = self.db_object.type

        parking_taken_count = Aircraft.objects.filter(
                type=type_to_check, state='PARKED').count()

        if type_to_check == 'AIRLINER':
            PARKING_PLACES = get_setting('AIRPORT_LARGE_PARKING_SPOTS', 10)
        else:
            PARKING_PLACES = get_setting('AIRPORT_SMALL_PARKING_SPOTS', 5)

        if parking_taken_count >= PARKING_PLACES:
            from_state = ''
            if self.db_object:
                from_state = self.db_object.state
            raise StateConflict(
                aircraft=self.db_object,
                from_state=from_state,
                to_state=self.data['state'],
                description='No free parking spot'
            )


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


class StateChangeLogSerializer(serializers.ModelSerializer):
    aircraft = serializers.SlugRelatedField(many=False, read_only=True, slug_field='call_sign')

    class Meta:
        model = StateChangeLog
        fields = ('aircraft', 'from_state', 'to_state', 'outcome', 'description', 'time')

    def to_representation(self, obj):
        ret = super(StateChangeLogSerializer, self).to_representation(obj)
        call_sign = ret.pop('aircraft')
        ret['call_sign'] = call_sign

        return ret
