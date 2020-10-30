from django.utils import timezone

from celery import shared_task

import requests

from weather.models import WeatherData


@shared_task
def load_weather_data():
    res = requests.get(
        'http://api.openweathermap.org/data/2.5/weather',
        params={
            'q': 'Belgrade',
            'units': 'metric',
            'appid': '1a1f91e2241e9056cf2dd4f9cf66e8da'
        }
    )

    data = {
        'description': res.json()['weather'][0]['description'],
        'temperature': res.json()['main']['temp'],
        'visibility': res.json()['visibility'],
        'wind_speed': res.json()['wind']['speed'],
        'wind_deg': res.json()['wind']['deg'],
        'last_update': timezone.now()
    }

    if WeatherData.objects.all().count() == 0:
        WeatherData.objects.create(**data)
    else:
        WeatherData.objects.all().update(**data)
