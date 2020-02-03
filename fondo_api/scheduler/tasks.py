import logging
from celery.decorators import task, periodic_task
from celery.task.schedules import crontab
from datetime import datetime

from fondo_api.models import SchedulerTask
from fondo_api.scheduler.executers.factory import get_executer

logger = logging.getLogger(__name__)

@periodic_task(
    name = "Scheduler", 
    run_every = (crontab(minute=0, hour='10,14')), 
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