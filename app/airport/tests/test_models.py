from django.test import TestCase
from django.db.utils import IntegrityError

from airport.models import Aircraft


def create_aircraft(call_sign):
    aircraft = Aircraft.objects.create(
        call_sign='test_call',
        altitude=0,
        heading=0,
        longitude=0,
        latitude=0
    )

    return aircraft


class AircraftTest(TestCase):

    def test_aircraft_should_be_represented_by_call_sign(self):
        aircraft = create_aircraft(call_sign='test_call')

        self.assertEqual(str(aircraft), 'test_call')

    def test_call_sign_should_be_unique(self):
        CALL = 'NC9574'
        create_aircraft(call_sign=CALL)

        # check if fails to create same aircraft again
        with self.assertRaises(IntegrityError):
            create_aircraft(call_sign=CALL)

    def test_should_set_state_to_PARKED_if_not_defined(self):
        aircraft = create_aircraft(call_sign='ABCD')

        self.assertEqual(aircraft.state, 'PARKED')
