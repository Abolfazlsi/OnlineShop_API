# tasks.py
from celery import shared_task
from django.utils import timezone
from account.models import Otp


@shared_task
def delete_otp(pk):
    try:
        otp = Otp.objects.get(id=pk)
        otp.delete()
        print(f"Otp {pk} deleted successfully.")
    except Otp.DoesNotExist:
        print(f"Otp {pk} does not exist.")
