from django_celery_beat.models import PeriodicTask, IntervalSchedule
from datetime import timedelta

import account.tasks

schedule, created = IntervalSchedule.objects.get_or_create(
    every=1,
    period=IntervalSchedule.MINUTES,
)

PeriodicTask.objects.create(
    interval=schedule,
    name='Delete expired OTPs every minute',
    task=account.tasks.delete_expired_otps(),
)
