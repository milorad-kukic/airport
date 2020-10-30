from celery import shared_task

from airport.models import Aircraft


@shared_task
def ground_crew_routine():
    Aircraft.objects.filter(
            state=Aircraft.LANDED
    ).update(state=Aircraft.PARKED)
