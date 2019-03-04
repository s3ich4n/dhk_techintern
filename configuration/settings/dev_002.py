from .base import *  # noqa: F403

DEBUG = True
UNIT_TEST = True

INSTALLED_APPS += [

]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'calypso0823@gmail.com'
EMAIL_HOST_PASSWORD = 'RjT8rKmcYatfw3U'
EMAIL_USE_TLS = True

MIDDLEWARE += [
    # 디버깅 툴바

]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
]

# 불필요시 주석처리
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}
