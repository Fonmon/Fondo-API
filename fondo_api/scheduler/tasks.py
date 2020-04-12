import logging
from celery.decorators import task, periodic_task
from celery.task.schedules import crontab
from django.utils.timezone import make_aware
from datetime import datetime
from dateutil.relativedelta import relativedelta

from fondo_api.models import SchedulerTask
from fondo_api.scheduler.executers.factory import get_executer

logger = logging.getLogger(__name__)

@periodic_task(
    name = "Scheduler", 
    run_every = (crontab(minute=0, hour='10,14')), 
    # run_every = crontab(),
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
            create_repeat_instance(task)
        except Exception as ex:
            logger.error("Error processing task with id: {}, exception: {}".format(task.id, ex))

def create_repeat_instance(task):
    if task.repeat != 0:
        run_date = task.run_date
        if task.repeat == 1:
            run_date = run_date + relativedelta(days=1)
        if task.repeat == 2:
            run_date = run_date + relativedelta(weeks=1)
        if task.repeat == 3:
            run_date = run_date + relativedelta(months=1)
        if task.repeat == 4:
            run_date = run_date + relativedelta(years=1)

        # run_date = make_aware(run_date)
        SchedulerTask.objects.create(
            type = task.type,
            run_date = run_date,
            payload = task.payload,
            repeat = task.repeat
        )