from unittest.mock import patch

from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Aircraft


class AircraftPrivateApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_public_key_not_sent_should_return_401_unauthorized(self):
        SENT_CALL_SIGN = 'AB1234'
        payload = {
            'state': 'APPROACH'
        }

        res = self.client.post(f'/api/{SENT_CALL_SIGN}/intent/', payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('airport.views.public_key_is_valid')
    def test_invalid_public_key_should_return_401_unauthorized(self, public_key_is_valid):
        SENT_CALL_SIGN = 'AB1234'
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'invalid public key'
        }
        public_key_is_valid.return_value = False

        self.client.post(f'/api/{SENT_CALL_SIGN}/intent/', payload)

        saved_aircraft = Aircraft.objects.first()
        self.assertIsNone(saved_aircraft)

    @patch('airport.views.public_key_is_valid')
    def test_should_save_new_aircraft_if_valid_request_is_sent(self, public_key_is_valid):
        SENT_CALL_SIGN = 'NC9574'
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }
        public_key_is_valid.return_value = True

        self.client.post(f'/api/{SENT_CALL_SIGN}/intent/', payload)

        saved_aircraft = Aircraft.objects.get(call_sign=SENT_CALL_SIGN)
        self.assertEqual(saved_aircraft.call_sign, SENT_CALL_SIGN)

    @patch('airport.views.public_key_is_valid')
    def test_valid_take_off_request_should_return_204_no_content(self, public_key_is_valid):
        SENT_CALL_SIGN = 'AB1234'
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }
        public_key_is_valid.return_value = True

        res = self.client.post(f'/api/{SENT_CALL_SIGN}/intent/', payload)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(res.data)

    @patch('airport.views.public_key_is_valid')
    def test_known_aircraft_sends_valid_request_return_204_no_content(self, public_key_is_valid):
        aircraft = Aircraft.objects.create(call_sign='ABCD')
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }
        public_key_is_valid.return_value = True

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(res.data)

    @patch('airport.views.public_key_is_valid')
    def test_state_not_passed_return_400_bad_request(self, public_key_is_valid):
        aircraft = Aircraft.objects.create(call_sign='ABCD')
        payload = {
            'public_key': 'valid public key'
        }
        public_key_is_valid.return_value = True

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(res.data)

    ######################################
    # TESTS FOR VALID WORKFLOW SWITCHING #
    ######################################

    @patch('airport.views.public_key_is_valid')
    def test_aircraft_can_switch_state_from_PARKED_to_TAKE_OFF(self, public_key_is_valid):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='PARKED')
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }
        public_key_is_valid.return_value = True

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'TAKE_OFF')

    @patch('airport.views.public_key_is_valid')
    def test_aircraft_can_switch_state_from_TAKE_OFF_to_AIRBORNE(self, public_key_is_valid):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='TAKE_OFF')
        payload = {
            'state': 'AIRBORNE',
            'public_key': 'valid public key'
        }
        public_key_is_valid.return_value = True

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'AIRBORNE')

    @patch('airport.views.public_key_is_valid')
    def test_aircraft_can_switch_state_from_AIRBORNE_to_APPROACH(self, public_key_is_valid):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='AIRBORNE')
        payload = {
            'state': 'APPROACH',
            'public_key': 'valid public key'
        }
        public_key_is_valid.return_value = True

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'APPROACH')

    @patch('airport.views.public_key_is_valid')
    def test_aircraft_can_switch_state_from_APPROACH_to_LANDED(self, public_key_is_valid):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='APPROACH')
        payload = {
            'state': 'LANDED',
            'public_key': 'valid public key'
        }
        public_key_is_valid.return_value = True

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'LANDED')

    @patch('airport.views.public_key_is_valid')
    def test_aircraft_can_switch_state_from_APPROACH_to_AIRBORNE(self, public_key_is_valid):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='APPROACH')
        payload = {
            'state': 'AIRBORNE',
            'public_key': 'valid public key'
        }
        public_key_is_valid.return_value = True

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'AIRBORNE')

    ########################################
    # TESTS FOR INVALID WORKFLOW SWITCHING #
    ########################################

    @patch('airport.views.public_key_is_valid')
    def test_aircraft_cant_switch_state_from_PARKED_to_invalid_state(self, public_key_is_valid):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='PARKED')
        payload = {
            'state': 'INVALID STATE',
            'public_key': 'valid public key'
        }
        public_key_is_valid.return_value = True

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'PARKED')

    @patch('airport.views.public_key_is_valid')
    def test_PARKED_aircraft_cant_swith_to_other_state_than_TAKE_OFF(self, public_key_is_valid):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='PARKED')
        payload = {
            'state': 'APPROACH',
            'public_key': 'valid public key'
        }
        public_key_is_valid.return_value = True

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'PARKED')

    @patch('airport.views.public_key_is_valid')
    def test_TAKE_OFF_aircraft_cant_swith_to_other_state_than_AIRBORNE(self, public_key_is_valid):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='TAKE_OFF')
        payload = {
            'state': 'APPROACH',
            'public_key': 'valid public key'
        }
        public_key_is_valid.return_value = True

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'TAKE_OFF')

    @patch('airport.views.public_key_is_valid')
    def test_AIRBORNE_aircraft_cant_swith_to_other_state_than_APPROACH(self, public_key_is_valid):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='AIRBORNE')
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }
        public_key_is_valid.return_value = True

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'AIRBORNE')

    @patch('airport.views.public_key_is_valid')
    def test_APPROACH_aircraft_cant_swith_to_other_state_than_AIRBORNE_or_LANDED(self, public_key_is_valid):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='AIRBORNE')
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }
        public_key_is_valid.return_value = True

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'AIRBORNE')
