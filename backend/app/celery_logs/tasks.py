import time

from celery import shared_task
from celery.signals import task_prerun, task_success, task_failure
from app.celery_logs.models import CeleryLogs

task_execution_times = {}

@task_prerun.connect
def task_celery_prerun(sender=None, **kwargs):
    if not sender:
        pass

    CeleryLogs.objects.create(task_id=kwargs.get("task_id"), status="PENDING", task_name=sender.name)
    task_execution_times[kwargs["task_id"]] = time.time()


@task_success.connect
def task_celery_success(sender=None, **kwargs):
    if not sender or not task_execution_times.get(sender.request.id):
        pass

    end_time = time.time()
    CeleryLogs.objects.filter(task_id=kwargs["task_id"]).update(
        status="SUCCESS",
        process_time=end_time - task_execution_times[sender.request.id],
        message="SUCCESS",
    )


@task_failure.connect
def task_celery_fail(sender=None, **kwargs):
    if not sender or task_execution_times.get(sender.request.id):
        pass

    end_time = time.time()
    CeleryLogs.objects.filter(task_id=kwargs["task_id"]).update(
        status="FAIL",
        process_time=end_time - task_execution_times[sender.request.id],
        message=kwargs.get("einfo").exception,
    )