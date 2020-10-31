from unittest.mock import patch

from django.test import TestCase, override_settings

from rest_framework.test import APIClient

from airport.models import Aircraft, StateChangeLog


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


class StateChangeLogTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.patcher = patch('airport.permissions.IsValidPublicKey.has_permission')
        self.public_key_is_valid = self.patcher.start()
        self.public_key_is_valid.return_value = True

    def tearDown(self):
        self.patcher.stop()

    ########################################
    # TESTS FOR ACCEPTED STATE CHANGE LOGS #
    ########################################

    def test_known_aircraft_from_PARKED_to_TAKE_OFF_accepted_log(self):
        aircraft = create_aircraft('CS123', state='PARKED')

        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        logs = StateChangeLog.objects.all()
        self.assertEqual(len(logs), 1)
        log = logs[0]
        self.assertLog(log, aircraft, 'PARKED', 'TAKE_OFF', 'ACCEPTED')

    def test_known_aircraft_from_TAKE_OFF_to_AIRBORNE_accepted_log(self):
        aircraft = create_aircraft('CS123', state='TAKE_OFF')

        payload = {
            'state': 'AIRBORNE',
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        logs = StateChangeLog.objects.all()
        self.assertEqual(len(logs), 1)
        log = logs[0]
        self.assertLog(log, aircraft, 'TAKE_OFF', 'AIRBORNE', 'ACCEPTED')

    def test_known_aircraft_from_AIRBORNE_to_APPROACH_accepted_log(self):
        aircraft = create_aircraft('CS123', state='AIRBORNE')

        payload = {
            'state': 'APPROACH',
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        logs = StateChangeLog.objects.all()
        self.assertEqual(len(logs), 1)
        log = logs[0]
        self.assertLog(log, aircraft, 'AIRBORNE', 'APPROACH', 'ACCEPTED')

    def test_known_aircraft_from_APPROACH_to_LANDED_accepted_log(self):
        aircraft = create_aircraft('CS123', state='APPROACH')

        payload = {
            'state': 'LANDED',
            'public_key': 'dummy_public_key_that_we_consider_valid'
        }

        self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        logs = StateChangeLog.objects.all()
        self.assertEqual(len(logs), 1)
        log = logs[0]
        self.assertLog(log, aircraft, 'APPROACH', 'LANDED', 'ACCEPTED')

    ########################################
    # TESTS FOR REJECTED STATE CHANGE LOGS #
    ########################################

    def test_know_aircraft_invalid_state_change_from_PARKED_rejected_log(self):
        aircraft = create_aircraft(call_sign='AB1234', state='PARKED')
        payload = {
            'state': 'APPROACH',
            'public_key': 'valid public key'
        }

        self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        logs = StateChangeLog.objects.all()
        self.assertEqual(len(logs), 1)
        log = logs[0]
        self.assertLog(log, aircraft, 'PARKED', 'APPROACH', 'REJECTED')

    def test_know_aircraft_invalid_state_change_from_TAKE_OFF_rejected_log(self):
        aircraft = create_aircraft(call_sign='NC9574', state='TAKE_OFF')
        payload = {
            'state': 'LANDED',
            'public_key': 'valid public key'
        }

        self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        logs = StateChangeLog.objects.all()
        self.assertEqual(len(logs), 1)
        log = logs[0]
        self.assertLog(log, aircraft, 'TAKE_OFF', 'LANDED', 'REJECTED')

    #######################################
    # FAILURES DUE TO AIRPORT CONSTRAINTS #
    #######################################

    @override_settings(AIRPORT_RUNAWAYS=1)
    def test_runaway_take_rejected_log(self):
        create_aircraft(call_sign='A1', state='TAKE_OFF')
        aircraft = create_aircraft(call_sign='A2', state='PARKED')

        payload = {
            'state': 'TAKE_OFF',
            'public_key': 'valid public key'
        }

        self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        logs = StateChangeLog.objects.all()
        self.assertEqual(len(logs), 1)
        log = logs[0]
        self.assertLog(log, aircraft, 'PARKED', 'TAKE_OFF', 'REJECTED')

    @override_settings(AIRPORT_RUNAWAYS=1)
    def test_runaway_taken_APPROACH_to_LAND_rejected_log(self):
        create_aircraft(call_sign='A1', state='TAKE_OFF')
        aircraft = create_aircraft(call_sign='A2', state='APPROACH')

        payload = {
            'state': 'LANDED',
            'public_key': 'valid public key'
        }

        self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        logs = StateChangeLog.objects.all()
        self.assertEqual(len(logs), 1)
        log = logs[0]
        self.assertLog(log, aircraft, 'APPROACH', 'LANDED', 'REJECTED')

    def test_APPROACH_when_other_is_already_APPROACH_reject_log(self):
        create_aircraft(call_sign='A1', state='APPROACH')
        aircraft = create_aircraft(call_sign='A2', state='AIRBORNE')

        payload = {
            'state': 'APPROACH',
            'public_key': 'valid public key'
        }

        self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        logs = StateChangeLog.objects.all()
        self.assertEqual(len(logs), 1)
        log = logs[0]
        self.assertLog(log, aircraft, 'AIRBORNE', 'APPROACH', 'REJECTED')

    @override_settings(AIRPORT_LARGE_PARKING_SPOTS=3)
    def test_LANDED_when_no_parking_available_reject_log(self):
        create_aircraft(call_sign='cs1', state='PARKED', type='AIRLINER')
        create_aircraft(call_sign='cs2', state='PARKED', type='AIRLINER')
        create_aircraft(call_sign='cs3', state='PARKED', type='AIRLINER')

        aircraft = create_aircraft('CALL_123', state='APPROACH', type='AIRLINER')

        payload = {
            'state': 'LANDED',
            'public_key': 'valid public key'
        }

        self.client.post(f'/api/{aircraft.call_sign}/intent/', payload)

        logs = StateChangeLog.objects.all()
        self.assertEqual(len(logs), 1)
        log = logs[0]
        self.assertLog(log, aircraft, 'APPROACH', 'LANDED', 'REJECTED')

    #####################
    # CUSTOM ASSERTIONS #
    #####################

    def test_new_aircraft_added_success_log(self):
        CALL_SIGN = 'MK2408'
        payload = {
            'type': 'AIRLINER',
            'state': 'PARKED',
            'intent': 'TAKE_OFF',
            'public_key': 'valid public key'
        }

        self.client.post(f'/api/{CALL_SIGN}/intent/', payload)

        aircraft = Aircraft.objects.first()  # aircraft should be created

        logs = StateChangeLog.objects.all()
        self.assertEqual(len(logs), 1)
        log = logs[0]
        self.assertLog(log, aircraft, 'PARKED', 'TAKE_OFF', 'ACCEPTED')

    #####################
    # CUSTOM ASSERTIONS #
    #####################

    def assertLog(self, log, expected_aircraft, expected_from_state, expected_to_state, expected_outcome):
        self.assertEqual(log.aircraft, expected_aircraft)
        self.assertEqual(log.from_state, expected_from_state)
        self.assertEqual(log.to_state, expected_to_state)
        self.assertEqual(log.outcome, expected_outcome)
