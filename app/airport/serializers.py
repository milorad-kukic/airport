from rest_framework import serializers

from airport.models import Aircraft


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
