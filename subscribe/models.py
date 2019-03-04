from django.contrib.auth.models import User
from django.db import models


class Subscriber(models.Model):
    subscriber = models.OneToOneField(
        User,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='subscriber_of',
    )

    # 이메일 구독관련 flag(is_subscribed, subscribing_email)
    is_subscribed = models.BooleanField(default=False)
    subscribing_email = models.EmailField(default='', blank=True, unique=True)
