from django.forms.models import model_to_dict

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from weather.models import WeatherData
from weather.serializers import WeatherDataSerializer


class WeatherViewSet(viewsets.GenericViewSet):

    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer

    @action(methods=['get'], detail=False,
            url_path='(?P<call_sign>[^/.]+)/weather',
            url_name='weather')
    def weather(self, request, call_sign=None, *args):
        weather_data = WeatherData.objects.first()

        if not weather_data:
            return Response({'error': 'invalid'})

        serializer = self.get_serializer(data=model_to_dict(weather_data))

        if serializer.is_valid():
            return Response(serializer.data)
        else:
            print(serializer.errors)
            return Response({'error': 'invalid'})
