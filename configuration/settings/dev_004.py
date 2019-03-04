from .base import *  # noqa: F403

DEBUG = True
UNIT_TEST = True

INSTALLED_APPS += [  # noqa: F405
    # 공통
    'debug_toolbar',
    'django_extensions',

]

MIDDLEWARE += [  # noqa: F405
    # 디버깅 툴바
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# 이설정은 디버깅 툴바 기본 설정으로 아래 설정이 주석처리 되어도 기본적으로 적용되있습니다.
# 학습 목적에서 적어놨으니 익숙해지면 나중에 지우겠습니다.
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]
# 디버깅 툴바가 접근 가능한 내부 허용 ip_Set
INTERNAL_IPS = ('127.0.0.1',)

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

# Email 관련 옵션
# 추후 딜리버리히어로에서 사용하려면
# 관련 권한을 얻아야 하기때문에 임시 설정을 이곳에 두었습니다.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'l4in.mailtest@gmail.com'
EMAIL_HOST_PASSWORD = 'epgfqbzezidkfbxo'
