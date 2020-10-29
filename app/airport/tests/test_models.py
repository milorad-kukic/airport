from django.test import TestCase
from django.db.utils import IntegrityError

from airport.models import Aircraft


class AircraftTest(TestCase):

    def test_aircraft_should_be_represented_by_call_sign(self):
        aircraft = Aircraft(call_sign='test_call')

        self.assertEqual(str(aircraft), 'test_call')

    def test_call_sign_should_be_unique(self):
        CALL = 'NC9574'
        Aircraft.objects.create(call_sign=CALL)

        # check if fails to create same aircraft again
        with self.assertRaises(IntegrityError):
            Aircraft.objects.create(call_sign=CALL)

    def test_should_set_state_to_PARKED_if_not_defined(self):
        aircraft = Aircraft.objects.create(call_sign='ABCD')

        self.assertEqual(aircraft.state, 'PARKED')
