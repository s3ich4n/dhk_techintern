from django.urls import path

from subscribe.views import email_subscribe

app_name = 'subscribe'
urlpatterns = [
    path('email/', email_subscribe.EmailSubscribe.as_view(), name='email-subscribe'),
]
