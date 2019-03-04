from http import HTTPStatus

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse


class AuthenticationMixinTestCase(TestCase):

    # 로그인 된 상황에서 api 요청이 정상적으로 반환하는지를 테스트
    def test_logined_user_request_api_view_extends_loginedMixin(self):
        # given
        username = 'new_user'
        password = 'django_password'

        if User.objects.filter(username=username).exists():
            User.objects.filter(username=username).delete()

        User.objects.create_user(
            username=username,
            password=password,
            email='',
        )
        self.client.login(username=username, password=password)

        # when
        response = self.client.get(reverse('account:mixin_test_api'))

        # then
        self.assertNotEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_not_logined_user_request_api_view_extends_loginRequiredMixin(self):
        # given
        # no login!!!

        # when
        response = self.client.get(reverse('account:mixin_test_api'))

        # then
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertEqual(response.json()['message'], '인증되지 않은 사용자입니다')


class AuthorizationRequiredMixinTestCase(TestCase):

    def test_has_permission_user_request_api_view_extends_PermissionRequiredMixin(self):
        # Given
        username = 'user_has_permissions'
        password = 'django_password'
        if User.objects.filter(username=username).exists():
            User.objects.filter(username=username).delete()

        user_has_no_permissions = User.objects.create_user(
            username=username,
            password=password,
            email=''
        )

        user_has_no_permissions.user_permissions.add(
            Permission.objects.get(codename='view_event')
        )

        user_has_no_permissions.save()
        self.client.login(username=username, password=password)

        # When
        response = self.client.get(reverse('account:mixin_test_api'))

        # Then
        self.assertNotEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_has_no_permission_user_api_view_extends_PermissionRequiredMixin(self):
        # Given
        username = 'no_permissions_user'
        password = 'django_password'
        if User.objects.filter(username=username).exists():
            User.objects.filter(username=username).delete()

        user_has_permissions = User.objects.create_user(
            username=username,
            password=password,
            email=''
        )

        # remove Permission view_event
        user_has_permissions.user_permissions.remove(
            Permission.objects.get(codename='view_event')
        )

        user_has_permissions.save()
        self.client.login(username=username, password=password)

        # When
        response = self.client.get(reverse('account:mixin_test_api'))

        # Then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json()['message'], '해당요청에 권한이 없습니다')
