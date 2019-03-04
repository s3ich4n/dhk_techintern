from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from subscribe.models import Subscriber
from subscribe.tests import logged_in_account_maker


class TestUnsubscribe(TestCase):

    @classmethod
    def setUpClass(cls):
        User = get_user_model()

        super(TestUnsubscribe, cls).setUpClass()

        cls.url = reverse('subscribe:email-subscribe')
        cls.password = 'll44iinn!!'

    # what happens when a valid value unsubscribed successfully?
    def test_api_call_after_deletion_should_return_ok_status(self):
        # GIVEN
        subscribed_account = logged_in_account_maker(self, f'subscriber@{settings.DOMAIN}')

        Subscriber.objects.create(
            subscriber=subscribed_account,
            is_subscribed=True,
        )

        # WHEN
        response = self.client.delete(
            self.url,
        )

        # THEN
        self.assertEqual(response.status_code, HTTPStatus.OK)
