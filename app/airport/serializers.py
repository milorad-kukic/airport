from rest_framework import serializers

from airport.models import Aircraft


class AircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = ('id', 'call_sign')
        read_only_fields = ('id',)
