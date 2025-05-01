from django.core.management.base import BaseCommand
from account.models import Otp
from datetime import datetime, timedelta
import pytz


class Command(BaseCommand):
    help = "Remove expired otp codes"

    def handle(self, *args, **options):
        expired_time = datetime.now(tz=pytz.timezone("Asia/Tehran")) - timedelta(minutes=2)
        Otp.objects.filter(created__lt=expired_time).delete()
        self.stdout.write("all expired otp codes removed.")
