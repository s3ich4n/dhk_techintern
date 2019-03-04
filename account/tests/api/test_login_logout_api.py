from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginLogoutTestCase(TestCase):
    fixtures = ['user.json', ]

    def setUp(self):
        self.username = 'sky5367'
        self.password = 'django_password'
        User.objects.filter(username=self.username).delete()
        User.objects.create_user(username=self.username, password=self.password, email='')

        response = self.client.get('/')
        self.csrf_token = response.cookies.get('csrftoken')

    def test_normal_logout(self):
        # Given
        self.client.login(username=self.username, password=self.password)

        # When
        response = self.client.get(reverse('account:logout_api'))

        # Then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()['message'], '로그아웃 되었습니다')
