import datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from subscribe.models import Subscriber
from subscribe.scripts.parse_holiday_data import weekend_distinction


class TestEmailSending(TestCase):

    @classmethod
    def setUpClass(cls):
        User = get_user_model()

        super(TestEmailSending, cls).setUpClass()

        cls.subscribed_account = User.objects.create(
            username='test_user',
            email='subscriber@rgpkorea.co.kr',
            password='ll44iinn!!',
        )
        Subscriber.objects.create(subscriber=cls.subscribed_account)
        cls.client = Client()
        cls.url = reverse('subscribe:email-subscribe')

    @patch('django.core.mail.send_mail')
    def test_weekend_should_not_send_an_email_to_subscriber(self, mock_email):
        # GIVEN
        weekend_2018 = datetime.datetime(2018, 12, 1)

        # WHEN
        is_weekend = weekend_distinction(weekend_2018)

        # THEN
        self.assertEqual(is_weekend, False)
        self.assertFalse(mock_email.called)

    @patch('django.core.mail.send_mail')
    def test_holiday_on_week_should_not_send_an_email_to_subscriber(self, mock_email):
        # GIVEN
        christmas_2018 = datetime.datetime(2018, 12, 25)

        # WHEN
        is_weekday = weekend_distinction(christmas_2018)

        # THEN
        self.assertEqual(is_weekday, True)
        self.assertFalse(mock_email.called)

    @patch('django.core.mail.send_mail')
    def test_weekday_should_send_an_email_to_subscriber(self, mock_email):
        # GIVEN
        weekday_2018 = datetime.datetime(2018, 11, 28)

        # WHEN
        is_weekday = weekend_distinction(weekday_2018)

        # THEN
        self.assertEqual(is_weekday, True)
        self.assertFalse(mock_email.called)
