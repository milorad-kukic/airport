from django.test import TestCase

from airport.models import Aircraft, StateChangeLog
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

    def test_parked_aircraft_creates_success_log(self):
        aircraft = create_aircraft(
            call_sign='CS1',
            type='AIRLINER',
            state=Aircraft.LANDED
        )

        ground_crew_routine()

        aircraft.refresh_from_db()

        logs = StateChangeLog.objects.all()
        self.assertEqual(len(logs), 1)
        self.assertLog(logs[0], aircraft, 'LANDED', 'PARKED', 'ACCEPTED')

    def assertLog(self, log, expected_aircraft, expected_from_state, expected_to_state, expected_outcome):
        self.assertEqual(log.aircraft, expected_aircraft)
        self.assertEqual(log.from_state, expected_from_state)
        self.assertEqual(log.to_state, expected_to_state)
        self.assertEqual(log.outcome, expected_outcome)
