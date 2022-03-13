from __future__ import absolute_import
from celery import Celery
from celery.schedules import crontab

app = Celery('api')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(['fondo_api.scheduler'])
app.conf.beat_schedule = {
    'scheduler': {
        'schedule': crontab(minute=0, hour='10,14'),
        'task': 'scheduler'
    }
}