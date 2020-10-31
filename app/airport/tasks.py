from celery import shared_task

from airport.models import Aircraft, StateChangeLog


@shared_task
def ground_crew_routine():
    aircraft = Aircraft.objects.filter(
            state=Aircraft.LANDED
    ).first()

    if aircraft:
        aircraft.state = Aircraft.PARKED
        aircraft.save()

        StateChangeLog.objects.create(
            aircraft=aircraft,
            from_state=Aircraft.LANDED,
            to_state=Aircraft.PARKED,
            outcome='ACCEPTED',
            description='Paked by ground crew'
        )
