from django.test import TestCase

from airport.models import Aircraft
from airport.tasks import ground_crew_routine


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


class GroundCrewRoutineTests(TestCase):

    def test_landed_aircraft_parked(self):
        aircraft = create_aircraft(
            call_sign='CS1',
            type='AIRLINER',
            state=Aircraft.LANDED
        )

        ground_crew_routine()

        aircraft.refresh_from_db()

        self.assertEqual(aircraft.state, Aircraft.PARKED)
