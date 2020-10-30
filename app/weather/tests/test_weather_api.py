from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Aircraft

from weather.models import WeatherData


def create_aircraft(call_sign, state='PARKED', type='AIRLINER', longitude=0,
                    latitude=0, altitude=0, heading=0):
    return Aircraft.objects.create(
        call_sign=call_sign,
        state=state,
        type=type,
        longitude=longitude,
        latitude=latitude,
        altitude=altitude,
        heading=heading
    )


class WeatherApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_should_return_error_for_unknown_aircraft(self):
        UNKNOWN_CALL = 'UC666'

        res = self.client.get(f'/api/{UNKNOWN_CALL}/weather/')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wind_data_is_packed_togather(self):
        date_update = timezone.now()
        data = WeatherData.objects.create(
            description="Clear sky",
            temperature=11,
            visibility=1000,
            wind_speed=2,
            wind_deg=120,
            last_update=date_update
        )

        aircraft = create_aircraft(call_sign='CS123')

        res = self.client.get(f'/api/{aircraft.call_sign}/weather/')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['wind'],
            {
                'speed': data.wind_speed,
                'deg': data.wind_deg
            }
        )
