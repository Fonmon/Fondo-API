import logging
import requests
import json
import os
from celery.decorators import task, periodic_task
from celery.task.schedules import crontab
from datetime import datetime

import fondo_api.logic.notifications_logic as notifications_logic
from fondo_api.models import SchedulerTask
from fondo_api.scheduler.executers.factory import get_executer

logger = logging.getLogger(__name__)

@task(name = "send_notification")
def send_notification(message):
    logger.info("Sending request to MNS...")
    mns_host = os.environ.get('MNS_HOST', 'localhost')
    try:
        request = requests.post('http://{}:9901/mns/send'.format(mns_host), \
            data = json.dumps(message['content']), \
            headers = { 'content-type': 'application/json' }, \
            timeout = 120 \
        )
        # remove invalid subscriptions
        if request.status_code == requests.codes.ok:
            invalid_subscriptions = request.json()['invalid']
            notifications_logic.remove_invalid_subscriptions(invalid_subscriptions)
    except Exception as ex:
        logger.error("Error trying to connect to MNS service: {}".format(ex))

@periodic_task(
    name = "Scheduler", 
    run_every = (crontab(minute=0, hour='9,14')), 
    ignore_result = True)
def scheduler():
    logger.info("Running scheduler")

    date = datetime.now()
    tasks = SchedulerTask.objects.filter(run_date__year = date.year,
                                         run_date__month = date.month,
                                         run_date__day = date.day, processed = False)
    logger.info("{} tasks to process".format(len(tasks)))
    for task in tasks:
        try:
            executer = get_executer(task.type)
            executer.run(task.payload)
            task.processed = True
            task.save()
        except Exception as ex:
            logger.error("Error processing task with id: {}, exception: {}".format(task.id, ex))