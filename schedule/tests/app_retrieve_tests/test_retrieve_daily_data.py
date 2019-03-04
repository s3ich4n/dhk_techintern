import datetime
from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RetrieveDailyDataTest(TestCase):

    def setUp(self):
        username = 'root'
        password = 'django_password'
        User.objects.filter(username=username).delete()
        User.objects.create_superuser(username=username, password=password, email='')

        self.client.login(username='root', password='django_password')

        self.url = reverse('schedule:api-retrieve-monthly-value')
        self.start_date = datetime.date(2018, 10, 28)
        self.end_date = datetime.date(2018, 12, 9)
        self.weird_year = "20018/10/31"
        self.weird_month = "2018/13/09"
        self.weird_day = "2018/10/32"

    def test_data_should_be_within_year_area(self):
        # GIVEN
        test_urls_with_weird_year = \
            f'{self.weird_year}/?start={self.start_date}&end={self.end_date}'

        # WHEN
        response = self.client.get(
            self.url + test_urls_with_weird_year
        )

        # THEN
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_data_should_be_within_month_area(self):
        # GIVEN
        test_urls_with_weird_month = \
            f'{self.weird_month}/?start={self.start_date}&end={self.end_date}'

        # WHEN
        response = self.client.get(
            self.url + test_urls_with_weird_month
        )

        # THEN
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_data_should_be_within_day_area(self):
        # GIVEN
        test_urls_with_weird_day = \
            f'{self.weird_day}/?start={self.start_date}&end={self.end_date}'

        # WHEN
        response = self.client.get(
            self.url + test_urls_with_weird_day
        )

        # THEN
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
