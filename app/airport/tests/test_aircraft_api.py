from unittest.mock import patch

from django.test import TestCase, override_settings

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Aircraft


class AircraftPrivateApiInvalidKeyTests(TestCase):

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


class AircraftPrivateApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.patcher = patch('airport.views.public_key_is_valid')
        self.public_key_is_valid = self.patcher.start()
        self.public_key_is_valid.return_value = True

    def tearDown(self):
        self.patcher.stop()

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
        self.assertIsNone(res.data)

    def test_known_aircraft_sends_valid_request_return_204_no_content(self):
        aircraft = Aircraft.objects.create(call_sign='ABCD')
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(res.data)

    def test_state_not_passed_return_400_bad_request(self):
        aircraft = Aircraft.objects.create(call_sign='ABCD')
        payload = {
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(res.data)

    ######################################
    # TESTS FOR VALID WORKFLOW SWITCHING #
    ######################################

    def test_aircraft_can_switch_state_from_PARKED_to_TAKE_OFF(self):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='PARKED')
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }
        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'TAKE_OFF')

    def test_aircraft_can_switch_state_from_TAKE_OFF_to_AIRBORNE(self):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='TAKE_OFF')
        payload = {
            'state': 'AIRBORNE',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'AIRBORNE')

    def test_aircraft_can_switch_state_from_AIRBORNE_to_APPROACH(self):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='AIRBORNE')
        payload = {
            'state': 'APPROACH',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'APPROACH')

    def test_aircraft_can_switch_state_from_APPROACH_to_LANDED(self):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='APPROACH')
        payload = {
            'state': 'LANDED',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'LANDED')

    def test_aircraft_can_switch_state_from_APPROACH_to_AIRBORNE(self):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='APPROACH')
        payload = {
            'state': 'AIRBORNE',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'AIRBORNE')

    ########################################
    # TESTS FOR INVALID WORKFLOW SWITCHING #
    ########################################

    def test_aircraft_cant_switch_state_from_PARKED_to_invalid_state(self):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='PARKED')
        payload = {
            'state': 'INVALID STATE',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'PARKED')

    def test_PARKED_aircraft_cant_swith_to_other_state_than_TAKE_OFF(self):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='PARKED')
        payload = {
            'state': 'APPROACH',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'PARKED')

    def test_TAKE_OFF_aircraft_cant_swith_to_other_state_than_AIRBORNE(self):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='TAKE_OFF')
        payload = {
            'state': 'APPROACH',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'TAKE_OFF')

    def test_AIRBORNE_aircraft_cant_swith_to_other_state_than_APPROACH(self):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='AIRBORNE')
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'AIRBORNE')

    def test_APPROACH_aircraft_cant_swith_to_other_state_than_AIRBORNE_or_LANDED(self):
        aircraft = Aircraft.objects.create(call_sign='AB1234', state='AIRBORNE')
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'AIRBORNE')

    #################################
    # TESTS FOR AIRPORT CONSTRAINTS #
    #################################

    @override_settings(AIRPORT_RUNAWAYS=1)
    def test_only_one_aircraft_can_be_on_the_runway(self):
        Aircraft.objects.create(call_sign='A1', state='TAKE_OFF')
        aircraft = Aircraft.objects.create(call_sign='A2', state='PARKED')

        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'PARKED')

    @override_settings(AIRPORT_RUNAWAYS=1)
    def test_APPROACH_cant_go_to_LAND_if_aircraft_on_runway(self):
        Aircraft.objects.create(call_sign='A1', state='TAKE_OFF')
        aircraft = Aircraft.objects.create(call_sign='A2', state='APPROACH')

        payload = {
            'state': 'LANDED',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'APPROACH')

    @override_settings(AIRPORT_RUNAWAYS=1)
    def test_APPROACH_cant_go_to_LAND_if_other_aircraft_LANDED(self):
        Aircraft.objects.create(call_sign='A1', state='LANDED')
        aircraft = Aircraft.objects.create(call_sign='A2', state='APPROACH')

        payload = {
            'state': 'LANDED',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'APPROACH')
