from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase


class RetreiveMonthlyDataTest(TestCase):

    def setUp(self):
        username = 'root'
        password = 'django_password'
        User.objects.filter(username=username).delete()
        User.objects.create_superuser(username=username, password=password, email='')

        self.client.login(username='root', password='django_password')
        self.url = '/schedule/events/'


def test_api_should_return_400_when_api_recieves_weird_keys(self):
    # GIVEN
    request_with_weird_key = {
        'weird1': '2018-11-07',
        'weird2': '2018-11-09',
    }

    # WHEN
    response = self.client.get(
        self.url,
        request_with_weird_key,
    )

    # THEN
    self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


def test_api_should_return_400_when_api_recieves_weird_values(self):
    # GIVEN
    request_with_weird_value = {
        'start': '123-123-123',
        'end': '123-456-789',
    }

    # WHEN
    response = self.client.get(
        self.url,
        request_with_weird_value,
    )

    # THEN
    self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


def test_date_value_should_follow_calendar_order(self):
    # GIVEN
    request_with_upside_down_value = {
        'start': '2018-12-31',
        'end': '2018-01-01',
    }

    # WHEN
    response = self.client.get(
        self.url,
        request_with_upside_down_value
    )

    # THEN
    self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


def test_api_should_return_404_when_date_value_does_not_exist(self):
    # GIVEN
    startday_with_no_schedule = {
        'start': '2009-09-03',
        'end': '2009-09-03',
    }

    # WHEN
    response = self.client.get(
        self.url,
        startday_with_no_schedule,
    )

    # THEN
    self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
