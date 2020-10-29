from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Aircraft


class AircraftPrivateAPI(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_should_save_new_aircraft_if_valid_request_is_sent(self):
        SENT_CALL_SIGN = 'NC9574'
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        self.client.post(f'/api/{SENT_CALL_SIGN}/intent/', payload)

        saved_aircraft = Aircraft.objects.get(call_sign=SENT_CALL_SIGN)
        self.assertEqual(saved_aircraft.call_sign, SENT_CALL_SIGN)

    def test_valid_take_off_request_should_return_204_no_content(self):
        SENT_CALL_SIGN = 'AB1234'
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        res = self.client.post(f'/api/{SENT_CALL_SIGN}/intent/', payload)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
