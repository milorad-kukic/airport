from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Aircraft, StateChangeLog
from airport.serializers import StateChangeLogSerializer


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


def create_log(aircraft, from_state, to_state, outcome, description=""):
    return StateChangeLog.objects.create(
        aircraft=aircraft,
        from_state=from_state,
        to_state=to_state,
        outcome=outcome,
        description=description
    )


class StateChangeLogApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_can_retrieve_logs(self):
        aircraft1 = create_aircraft('A1', state='PARKED', type='AIRLINER')
        aircraft2 = create_aircraft('A2', state='PARKED', type='AIRLINER')

        log1 = create_log(aircraft1, 'PARKED', 'TAKE_OFF', 'ACCEPTED')
        log2 = create_log(aircraft1, 'TAKE_OFF', 'LANDED', 'REJECTED', description='Not a valid state change')
        log3 = create_log(aircraft2, 'PARKED', 'TAKE_OFF', 'ACCEPTED')

        res = self.client.get('/api/state_logs/')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serialized_log1 = StateChangeLogSerializer(log1)
        serialized_log2 = StateChangeLogSerializer(log2)
        serialized_log3 = StateChangeLogSerializer(log3)

        self.assertIn(serialized_log1.data, res.data)
        self.assertIn(serialized_log2.data, res.data)
        self.assertIn(serialized_log3.data, res.data)

    def test_can_limit_results_count_and_retrieve_latest(self):
        aircraft1 = create_aircraft('A1', state='PARKED', type='AIRLINER')
        aircraft2 = create_aircraft('A2', state='PARKED', type='AIRLINER')

        log1 = create_log(aircraft1, 'PARKED', 'TAKE_OFF', 'ACCEPTED')
        log2 = create_log(aircraft1, 'TAKE_OFF', 'LANDED', 'REJECTED', description='Not a valid state change')
        log3 = create_log(aircraft2, 'PARKED', 'TAKE_OFF', 'ACCEPTED')
        log4 = create_log(aircraft1, 'TAKE_OFF', 'APPROACH', 'REJECTED', description='Not a valid state change')

        res = self.client.get('/api/state_logs/?limit=2')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serialized_log1 = StateChangeLogSerializer(log1)
        serialized_log2 = StateChangeLogSerializer(log2)
        serialized_log3 = StateChangeLogSerializer(log3)
        serialized_log4 = StateChangeLogSerializer(log4)

        self.assertNotIn(serialized_log1.data, res.data['results'])
        self.assertNotIn(serialized_log2.data, res.data['results'])
        self.assertIn(serialized_log3.data, res.data['results'])
        self.assertIn(serialized_log4.data, res.data['results'])
