from celery import shared_task


@shared_task
def ground_crew_routine():
    print('do ground crew stuff')
