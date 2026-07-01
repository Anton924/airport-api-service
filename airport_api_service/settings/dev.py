from airport_api_service.settings.base import *

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS += ["debug_toolbar"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = [
    "127.0.0.1",
]

