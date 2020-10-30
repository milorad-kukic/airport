import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'every-minute': {
        'task': 'airport.tasks.ground_crew_routine',
        'schedule': 60
    },
    'every-5-minuts': {
        'task': 'weather.tasks.load_weather_data',
        'schedule': 300
    }
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
