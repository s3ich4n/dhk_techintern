from django.contrib.auth.models import User
from django.test import TestCase
from social_django.models import DjangoStorage, UserSocialAuth
from social_django.strategy import DjangoStrategy

from account.pipeline import add_permissions_user
from subscribe.models import Subscriber


class CustomPipelineTestCase(TestCase):

    def test_pipeline_add_permissions_user(self):
        # Given
        # 구글+ API가 보내준 개인 정보
        # FIXME: Sensitive info
        self.details = {
            'username': '',
            'email': '',
            'fullname': '',
            'first_name': '',
            'last_name': '',
        }
        # social_core.pipeline.user.create_user 파이프라인에서 생성된 객체
        django_user = User.objects.create(
            username=self.details['username'],
            email=self.details['email']
        )
        # social_core.pipeline.social_auth.social_user 파이프라인에서 생성된 객체
        social_user = UserSocialAuth.objects.create(
            user=django_user,
            provider='google-oauth2',
            uid=self.details['email'],
        )
        # social_core.pipeline.user.create_user 파이프라인에서 이미 존재하는 회원인지 검사하고 아래 인자값을 넘겨준다
        is_new = True

        storage = DjangoStorage()
        storage.user = social_user

        strategy = DjangoStrategy(storage=storage)

        # When
        pipeline_result = add_permissions_user(strategy=strategy, backend=None, details=self.details,
                                               is_new=is_new)

        # Then
        self.assertEqual(pipeline_result['user'].get_all_permissions(),
                         User.objects.get(username=self.details['username']).get_all_permissions())
        self.assertTrue(Subscriber.objects.filter(subscriber=pipeline_result['user']).exists())
