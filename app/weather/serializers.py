from rest_framework import serializers

from weather.models import WeatherData


class WeatherDataSerializer(serializers.ModelSerializer):

    wind = serializers.SerializerMethodField()

    class Meta:
        model = WeatherData
        fields = ('description', 'temperature', 'visibility',
                  'wind', 'wind_speed', 'wind_deg', 'last_update')

    def get_wind(self, obj):
        return {
            'speed': obj.get('wind_speed', None),
            'deg': obj.get('wind_deg', None)
        }

    def to_representation(self, obj):
        ret = super(WeatherDataSerializer, self).to_representation(obj)
        ret.pop('wind_speed')
        ret.pop('wind_deg')

        return ret
