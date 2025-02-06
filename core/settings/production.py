from core.settings.base import *

DEBUG = False

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'onlineshop_db',
        'USER': 'onlineshop_user',
        'PASSWORD': 'admin',
        'HOST': 'db',
        'PORT': '5432',
    }
}

STATIC_URL = 'public/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')
