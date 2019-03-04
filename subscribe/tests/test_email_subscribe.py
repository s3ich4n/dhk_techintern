from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from subscribe.models import Subscriber
from subscribe.tests import logged_in_account_maker


class TestSubscriberEmailValidation(TestCase):

    @classmethod
    def setUpClass(cls):
        User = get_user_model()

        super(TestSubscriberEmailValidation, cls).setUpClass()

        cls.mail_ignoring_rules_no_prefix = 'bad_email@'
        cls.mail_ignoring_rules_no_postfix = '@bad_email'
        cls.mail_ignoring_rules_no_full_url = 'bad_email@bad_email'

        cls.mail_already_subscribed = f'subscriber@{settings.DOMAIN}'
        cls.mail_do_not_subscribe_yet = f'account_who_wants_to_subscribe@{settings.DOMAIN}'

        cls.subscribed_account_another_mails = f'alertyo_subscribe@mail.com'

        cls.password = 'll44iinn!!'

        cls.subscribed_account = User.objects.create_user(
            username='test_user',
            password=cls.password,
            email=f'subscriber@{settings.DOMAIN}',
        )
        Subscriber.objects.create(
            subscriber=cls.subscribed_account,
            subscribing_email=cls.subscribed_account_another_mails,
        )

        cls.url = reverse('subscribe:email-subscribe')

    def test_email_should_follow_the_right_email_form(self):
        # GIVEN
        no_prefix_account = logged_in_account_maker(self, self.mail_ignoring_rules_no_prefix)
        no_postfix_account = logged_in_account_maker(self, self.mail_ignoring_rules_no_postfix)
        no_full_url_account = logged_in_account_maker(self, self.mail_ignoring_rules_no_full_url)

        # WHEN
        no_prefix_response = self.client.post(
            self.url,
            {'email': no_prefix_account.email},
        )
        no_postfix_response = self.client.post(
            self.url,
            {'email': no_postfix_account.email},
        )
        no_full_url_response = self.client.post(
            self.url,
            {'email': no_full_url_account.email},
        )

        # THEN
        self.assertEqual(no_prefix_response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(no_postfix_response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(no_full_url_response.status_code, HTTPStatus.BAD_REQUEST)

    def test_alertyo_subscribing_email_address_should_be_only_one(self):
        # GIVEN
        already_subscribed_account = logged_in_account_maker(self, self.mail_already_subscribed)

        Subscriber.objects.create(
            subscriber=already_subscribed_account,
            is_subscribed=False,
            subscribing_email='',
        )

        # WHEN
        response = self.client.post(
            self.url,
            {'email': self.subscribed_account_another_mails},
        )

        # THEN
        self.assertEqual(response.status_code, HTTPStatus.CONFLICT)

    def test_alertyo_should_send_mails_if_it_wants_to_receive_with_unique_email(self):
        # GIVEN
        not_yet_subscribed_account = logged_in_account_maker(self, self.mail_do_not_subscribe_yet)
        not_yet_alertyo_subscribed_account = 'alertyo-mailing@mail.com'

        Subscriber.objects.create(
            subscriber=not_yet_subscribed_account,
            is_subscribed=False,
            subscribing_email='',
        )

        # WHEN
        response = self.client.post(
            self.url,
            {'email': not_yet_alertyo_subscribed_account},
        )

        # THEN
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
