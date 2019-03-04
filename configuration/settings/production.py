from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    '*',
]

STATIC_ROOT = os.path.dirname(BASE_DIR)

# 이 형식으로 등록해야 함
DOMAIN = 'http://127.0.0.1:8000'

# 운영서버 환경변수로 등록
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '실 운용 계정',
        'PASSWORD': '실 운용 비밀번호',
        'HOST': ' 아이피 입력하기  ',
        'PORT': '5432',
    }
}
