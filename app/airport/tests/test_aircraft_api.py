from unittest.mock import patch

from django.test import TestCase, override_settings

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Aircraft
from airport.exceptions import InvalidPublicKey


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


class AircraftPrivateApiInvalidKeyTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.patcher = patch('airport.permissions.IsValidPublicKey.has_permission')
        self.public_key_is_valid = self.patcher.start()
        self.public_key_is_valid.return_value = False

    def tearDown(self):
        self.patcher.stop()

    def test_invalid_public_key_should_return_401_unauthorized(self):
        SENT_CALL_SIGN = 'AB1234'
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'invalid public key'
        }

        self.client.post(f'/api/{SENT_CALL_SIGN}/intent/', payload)

        saved_aircraft = Aircraft.objects.first()
        self.assertIsNone(saved_aircraft)


class AircraftPrivateApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.patcher = patch('airport.permissions.IsValidPublicKey.has_permission')
        self.public_key_is_valid = self.patcher.start()
        self.public_key_is_valid.return_value = True

    def tearDown(self):
        self.patcher.stop()

    def test_should_save_new_aircraft_if_valid_request_is_sent(self):
        SENT_CALL_SIGN = 'NC9574'
        payload = {
            'type': 'AIRLINER',
            'state': 'TAKE_OFF',
            'intent': 'AIRBORNE',
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        self.client.post(f'/api/{SENT_CALL_SIGN}/intent/', payload)

        saved_aircraft = Aircraft.objects.get(call_sign=SENT_CALL_SIGN)
        self.assertEqual(saved_aircraft.call_sign, SENT_CALL_SIGN)
        self.assertEqual(saved_aircraft.type, 'AIRLINER')

    def test_valid_take_off_request_should_return_204_no_content(self):
        CALL_SIGN = 'AB1234'
        create_aircraft(call_sign=CALL_SIGN, type='AIRLINER', state='PARKED')
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        res = self.client.post(f'/api/{CALL_SIGN}/intent/', payload)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(res.data)

    def test_known_aircraft_sends_valid_request_return_204_no_content(self):
        aircraft = create_aircraft(call_sign='ABCD')
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(res.data)

    def test_state_not_passed_return_400_bad_request(self):
        aircraft = create_aircraft(call_sign='ABCD')
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
        aircraft = create_aircraft(call_sign='AB1234', state='PARKED')
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }
        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'TAKE_OFF')

    def test_aircraft_can_switch_state_from_TAKE_OFF_to_AIRBORNE(self):
        aircraft = create_aircraft(call_sign='AB1234', state='TAKE_OFF')
        payload = {
            'state': 'AIRBORNE',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'AIRBORNE')

    def test_aircraft_can_switch_state_from_AIRBORNE_to_APPROACH(self):
        aircraft = create_aircraft(call_sign='AB1234', state='AIRBORNE')
        payload = {
            'state': 'APPROACH',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'APPROACH')

    def test_aircraft_can_switch_state_from_APPROACH_to_LANDED(self):
        aircraft = create_aircraft(call_sign='AB1234', state='APPROACH')
        payload = {
            'state': 'LANDED',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(aircraft.state, 'LANDED')

    def test_aircraft_can_switch_state_from_APPROACH_to_AIRBORNE(self):
        aircraft = create_aircraft(call_sign='AB1234', state='APPROACH')
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

    def test_aircraft_cValidationErrorant_switch_state_from_PARKED_to_invalid_state(self):
        aircraft = create_aircraft(call_sign='AB1234', state='PARKED')
        payload = {
            'state': 'INVALID STATE',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(aircraft.state, 'PARKED')

    def test_PARKED_aircraft_cant_swith_to_other_state_than_TAKE_OFF(self):
        aircraft = create_aircraft(call_sign='AB1234', state='PARKED')
        payload = {
            'state': 'APPROACH',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(res.data, None)
        self.assertEqual(aircraft.state, 'PARKED')

    def test_TAKE_OFF_aircraft_cant_swith_to_other_state_than_AIRBORNE(self):
        aircraft = create_aircraft(call_sign='AB1234', state='TAKE_OFF')
        payload = {
            'state': 'APPROACH',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(res.data, None)
        self.assertEqual(aircraft.state, 'TAKE_OFF')

    def test_AIRBORNE_aircraft_cant_swith_to_other_state_than_APPROACH(self):
        aircraft = create_aircraft(call_sign='AB1234', state='AIRBORNE')
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(res.data, None)
        self.assertEqual(aircraft.state, 'AIRBORNE')

    def test_APPROACH_aircraft_cant_swith_to_other_state_than_AIRBORNE_or_LANDED(self):
        aircraft = create_aircraft(call_sign='AB1234', state='AIRBORNE')
        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(res.data, None)
        self.assertEqual(aircraft.state, 'AIRBORNE')

    #################################
    # TESTS FOR AIRPORT CONSTRAINTS #
    #################################

    @override_settings(AIRPORT_RUNAWAYS=1)
    def test_only_one_aircraft_can_be_on_the_runway(self):
        create_aircraft(call_sign='A1', state='TAKE_OFF')
        aircraft = create_aircraft(call_sign='A2', state='PARKED')

        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(aircraft.state, 'PARKED')

    @override_settings(AIRPORT_RUNAWAYS=1)
    def test_APPROACH_cant_go_to_LAND_if_aircraft_on_runway(self):
        create_aircraft(call_sign='A1', state='TAKE_OFF')
        aircraft = create_aircraft(call_sign='A2', state='APPROACH')

        payload = {
            'state': 'LANDED',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(aircraft.state, 'APPROACH')

    @override_settings(AIRPORT_RUNAWAYS=1)
    def test_APPROACH_cant_go_to_LAND_if_other_aircraft_LANDED(self):
        create_aircraft(call_sign='A1', state='LANDED')
        aircraft = create_aircraft(call_sign='A2', state='APPROACH')

        payload = {
            'state': 'LANDED',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(aircraft.state, 'APPROACH')

    def test_only_one_aircraft_can_be_on_APPROACH(self):
        create_aircraft(call_sign='A1', state='APPROACH')
        aircraft = create_aircraft(call_sign='A2', state='AIRBORNE')

        payload = {
            'state': 'APPROACH',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(aircraft.state, 'AIRBORNE')

    @override_settings(AIRPORT_LARGE_PARKING_SPOTS=5)
    def test_AIRLINER_cant_land_if_no_large_parking_spot_available(self):
        create_aircraft(call_sign='cs1', state='PARKED', type='AIRLINER')
        create_aircraft(call_sign='cs2', state='PARKED', type='AIRLINER')
        create_aircraft(call_sign='cs3', state='PARKED', type='AIRLINER')
        create_aircraft(call_sign='cs4', state='PARKED', type='AIRLINER')
        create_aircraft(call_sign='cs5', state='PARKED', type='AIRLINER')

        aircraft = create_aircraft('CALL_123', state='APPROACH', type='AIRLINER')

        payload = {
            'state': 'LANDED',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(res.data)
        self.assertEqual(aircraft.state, 'APPROACH')

    @override_settings(AIRPORT_SMALL_PARKING_SPOTS=3)
    def test_PRIVATE_cant_land_if_no_small_parking_spot_available(self):
        create_aircraft(call_sign='cs1', state='PARKED', type='PRIVATE')
        create_aircraft(call_sign='cs2', state='PARKED', type='PRIVATE')
        create_aircraft(call_sign='cs3', state='PARKED', type='PRIVATE')

        aircraft = create_aircraft('CALL_123', state='APPROACH', type='PRIVATE')

        payload = {
            'state': 'LANDED',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        aircraft.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(res.data)
        self.assertEqual(aircraft.state, 'APPROACH')

    @override_settings(AIRPORT_LARGE_PARKING_SPOTS=3)
    def test_new_aircraft_with_no_state_cant_land_if_no_parking_spot_available(self):
        create_aircraft(call_sign='cs1', state='PARKED', type='AIRLINER')
        create_aircraft(call_sign='cs2', state='PARKED', type='AIRLINER')
        create_aircraft(call_sign='cs3', state='PARKED', type='AIRLINER')

        NEW_CALL_SIGN = 'MK2408'

        payload = {
            'state': 'LANDED',
            'type': 'AIRLINER',
            'public_key': 'valid public key'
        }

        res = self.client.post(f'/api/{NEW_CALL_SIGN}/intent/', payload)

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(res.data)
        self.assertFalse(Aircraft.objects.filter(call_sign=NEW_CALL_SIGN).exists())


class AircraftLocationTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.patcher = patch('airport.permissions.IsValidPublicKey.has_permission')
        self.public_key_is_valid = self.patcher.start()
        self.public_key_is_valid.return_value = True

    def tearDown(self):
        self.patcher.stop()

    def test_should_save_new_location_data_if_valid_request_is_sent(self):
        CALL_SIGN = 'NC9574'
        create_aircraft(call_sign=CALL_SIGN)

        payload = {
            'type': 'AIRLINER',
            'longitude': "20.455516172478386",
            'latitude': "44.82128505247063",
            'altitude': 3500,
            'heading': 220,
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        res = self.client.post(f'/api/{CALL_SIGN}/location/', payload)

        saved_aircraft = Aircraft.objects.get(call_sign=CALL_SIGN)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(saved_aircraft.altitude, 3500)

    def test_type_can_be_PRIVATE(self):
        CALL_SIGN = 'NC9574'
        create_aircraft(call_sign=CALL_SIGN, type='PRIVATE')

        payload = {
            'type': 'PRIVATE',
            'longitude': "20.455516172478386",
            'latitude': "44.82128505247063",
            'altitude': 4500,
            'heading': 220,
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        res = self.client.post(f'/api/{CALL_SIGN}/location/', payload)

        saved_aircraft = Aircraft.objects.get(call_sign=CALL_SIGN)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(saved_aircraft.altitude, 4500)

    def test_should_return_error_if_type_is_not_PRIVATE_or_AIRLINER(self):
        CALL_SIGN = 'NC9574'
        aircraft = create_aircraft(call_sign=CALL_SIGN)

        payload = {
            'type': 'UNKNOWN_TYPE',
            'longitude': "20.455516172478386",
            'latitude': "44.82128505247063",
            'altitude': 4500,
            'heading': 220,
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        res = self.client.post(f'/api/{CALL_SIGN}/location/', payload)

        saved_aircraft = Aircraft.objects.get(call_sign=CALL_SIGN)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(saved_aircraft, aircraft)

    def test_should_return_error_if_try_to_set_different_type(self):
        CALL_SIGN = 'NC9574'
        aircraft = create_aircraft(call_sign=CALL_SIGN, type='AIRLINER')

        payload = {
            'type': 'PRIVATE',
            'longitude': "20.455516172478386",
            'latitude': "44.82128505247063",
            'altitude': 4500,
            'heading': 220,
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        res = self.client.post(f'/api/{CALL_SIGN}/location/', payload)

        saved_aircraft = Aircraft.objects.get(call_sign=CALL_SIGN)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(saved_aircraft, aircraft)

    def test_type_param_is_mandatory(self):
        CALL_SIGN = 'NC9574'
        aircraft = create_aircraft(call_sign=CALL_SIGN)

        payload = {
            'longitude': "20.455516172478386",
            'latitude': "44.82128505247063",
            'altitude': 3500,
            'heading': 220,
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        res = self.client.post(f'/api/{CALL_SIGN}/location/', payload)

        saved_aircraft = Aircraft.objects.get(call_sign=CALL_SIGN)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(saved_aircraft, aircraft)

    def test_longitude_param_is_mandatory(self):
        CALL_SIGN = 'NC9574'
        aircraft = create_aircraft(call_sign=CALL_SIGN)

        payload = {
            'type': "AIRLINER",
            'latitude': "44.82128505247063",
            'altitude': 3500,
            'heading': 220,
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        res = self.client.post(f'/api/{CALL_SIGN}/location/', payload)

        saved_aircraft = Aircraft.objects.get(call_sign=CALL_SIGN)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(saved_aircraft, aircraft)

    def test_latitude_param_is_mandatory(self):
        CALL_SIGN = 'NC9574'
        aircraft = create_aircraft(call_sign=CALL_SIGN)

        payload = {
            'type': "AIRLINER",
            'longitude': "20",
            'altitude': 3500,
            'heading': 220,
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        res = self.client.post(f'/api/{CALL_SIGN}/location/', payload)

        saved_aircraft = Aircraft.objects.get(call_sign=CALL_SIGN)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(saved_aircraft, aircraft)

    def test_altitude_param_is_mandatory(self):
        CALL_SIGN = 'NC9574'
        aircraft = create_aircraft(call_sign=CALL_SIGN)

        payload = {
            'type': "AIRLINER",
            'longitude': "20.455516172478386",
            'latitude': "44.82128505247063",
            'heading': 220,
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        res = self.client.post(f'/api/{CALL_SIGN}/location/', payload)

        saved_aircraft = Aircraft.objects.get(call_sign=CALL_SIGN)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(saved_aircraft, aircraft)

    def test_heading_is_mandatory(self):
        CALL_SIGN = 'NC9574'
        aircraft = create_aircraft(call_sign=CALL_SIGN)

        payload = {
            'type': 'AIRLINER',
            'longitude': "20.455516172478386",
            'latitude': "44.82128505247063",
            'altitude': 3500,
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        res = self.client.post(f'/api/{CALL_SIGN}/location/', payload)

        saved_aircraft = Aircraft.objects.get(call_sign=CALL_SIGN)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(saved_aircraft, aircraft)


class LocationApiInvalidKeyTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.patcher = patch('airport.permissions.IsValidPublicKey.has_permission')
        self.public_key_is_valid = self.patcher.start()
        self.public_key_is_valid.side_effect = InvalidPublicKey

    def tearDown(self):
        self.patcher.stop()

    def test_invalid_public_key_should_return_401_unauthorized(self):
        CALL_SIGN = 'NC9574'
        aircraft = create_aircraft(call_sign=CALL_SIGN)

        payload = {
            'type': 'AIRLINER',
            'longitude': "20.455516172478386",
            'latitude': "44.82128505247063",
            'altitude': 3500,
            'heading': 220,
            'public_key': 'INVALID KEY'
        }

        res = self.client.post(f'/api/{CALL_SIGN}/location/', payload)

        saved_aircraft = Aircraft.objects.get(call_sign=CALL_SIGN)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(saved_aircraft, aircraft)
