import os

GOOGLE_CLIENT_ID = ""  # FIXME: remove sensitive data
GOOGLE_SECRET_KEY = ""  # FIXME: remove sensitive data

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6)6(e8yt1pzz*v!nxfxdol@ma-(p%*h_^sm-p860i#=+sgixx4'

STATIC_URL = '/static/'

DOMAIN = 'deliveryhero.co.kr'
SERVER_URL = 'http://127.0.0.1:8000'

STATICFILES_DIRS = [
    STATIC_DIR,
]
DEBUG = False
UNIT_TEST = False

# 이메일 관련 설정
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = ''  # FIXME: remove sensitive data
EMAIL_HOST_PASSWORD = ''  # FIXME: remove sensitive data
EMAIL_USE_TLS = True

# Application definition
INSTALLED_APPS = [
    # 날씨예보를 불러와서 저장하는 배치 프로그램이 담긴 앱
    'forecast.apps.ForecastConfig',
    # 스케줄러 관리 App
    'schedule.apps.ScheduleConfig',

    # 구독관리 App
    'subscribe.apps.SubscribeConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 프론트 static
    'bootstrap',
    'fontawesome',

    'account.apps.AccountConfig',
    'social_django',


]

SESSION_COOKIE_AGE = 3 * 60 * 60
LOGIN_URL = 'account/login/'

# Google OAuth2 settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = GOOGLE_CLIENT_ID
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = GOOGLE_SECRET_KEY
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
SOCIAL_AUTH_URL_NAMESPACE = 'social'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'account.pipeline.add_permissions_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',

)

AUTHENTICATION_BACKENDS = (
    # for Google authentication
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    # AlertYo 자체 인증
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'configuration.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            TEMPLATES_DIR,
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # social-oauth2
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'configuration.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'ko'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# weather planet API server
WEATHER_PLANET_API_KEY = ''  # FIXME: remove sensitive data
WEATHER_PLANET_SERVER_NAME = 'Weather Planet API server'
WEATHER_PLANET_URL = 'https://api2.sktelecom.com/weather/summary'
WEATHER_PLANET_API_VERSION = 2

# 기상청 크롤링
GISANG_TEMPERATURE_OBS = "07"
GISANG_WEATHER_OBS = "90"
GISANG_TEMP_PAGE_NAME = "기상청 날씨누리-평균기온"
GISANG_WEATHER_PAGE_NAME: str = "기상청 날씨누리-날씨"
GISANG_URL = "http://www.weather.go.kr/weather/climate/past_table.jsp"
GISANG_OLDEST_REFERENCE_YEAR = 1960

# 공휴일 정보 출력관련 상수
ENDPOINT_URL = \
    'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo'

OPENAPI_KEY = \
    ''  # FIXME: remove sensitive data
