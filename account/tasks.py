# tasks.py
from celery import shared_task
from django.utils import timezone
from account.models import Otp
from datetime import datetime, timedelta
import pytz


@shared_task
def delete_otp(pk):
    try:
        otp = Otp.objects.get(id=pk)
        otp.delete()
        print(f"Otp {pk} deleted successfully.")
    except Otp.DoesNotExist:
        print(f"Otp {pk} does not exist.")


@shared_task
def remove_expired_otp_codes():
    expired_time = datetime.now(tz=pytz.timezone("Asia/Tehran")) - timedelta(minutes=2)
    Otp.objects.filter(created__lt=expired_time).delete()
