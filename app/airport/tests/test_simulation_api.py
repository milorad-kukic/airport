from unittest.mock import patch

from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

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


class StartSimulationApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.patcher = patch('airport.permissions.IsValidPublicKey.has_permission')
        self.public_key_is_valid = self.patcher.start()
        self.public_key_is_valid.return_value = True

    def tearDown(self):
        self.patcher.stop()

    def test_should_delete_all_aircrafts_and_logs(self):
        aircraft1 = create_aircraft('A1')
        aircraft2 = create_aircraft('A2')
        StateChangeLog.objects.create(
            aircraft=aircraft1,
            from_state="LANDED",
            to_state="PARKED",
            outcome="SUCCESS",
            description=""
        )
        StateChangeLog.objects.create(
            aircraft=aircraft2,
            from_state="LANDED",
            to_state="PARKED",
            outcome="SUCCESS",
            description=""
        )

        payload = {
            "public_key": "Valid key"
        }

        res = self.client.post("/api/simulation/start/", payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(Aircraft.objects.all().count(), 0)
        self.assertEqual(StateChangeLog.objects.all().count(), 0)
