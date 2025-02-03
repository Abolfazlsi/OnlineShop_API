from core.settings.base import DJANGO_ENV
import os

from django.core.wsgi import get_wsgi_application

if DJANGO_ENV == 'production':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.production")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")

application = get_wsgi_application()
