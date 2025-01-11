from celery import shared_task
from django.utils import timezone
from account.models import Otp

@shared_task
def delete_expired_otps():
    expired_otps = Otp.objects.filter(expire__lt=timezone.now())
    count = expired_otps.count()
    expired_otps.delete()
    return f'Deleted {count} expired OTPs'
