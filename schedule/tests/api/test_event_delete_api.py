from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from schedule.models import Event


class EventDeleteAPITestCase(TestCase):
    fixtures = ['event.json', 'user.json', ]

    def setUp(self):
        self.client.login(username='root', password='django_password')
        response = self.client.get('/')
        self.csrf_token = response.cookies.get('csrftoken')

    def test_normal_event_request(self):
        # Given
        not_deleted_events = list(
            Event.objects.filter(deleted__isnull=True, end_at__gte=timezone.localtime())
        )
        header = {"csrftoken": self.csrf_token}

        for not_deleted_event in not_deleted_events:
            # When
            response = self.client.delete(
                reverse('schedule:event_api', kwargs={"id": not_deleted_event.id}), **header)

            # Then
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response.json()['message'], "요청이 정상적으로 처리되었습니다.")
            with self.assertRaises(Event.DoesNotExist):
                Event.objects.get(id=not_deleted_event.id, deleted__isnull=True)

    def test_already_deleted_event_request(self):
        # Given
        already_deleted_events_queryset = list(
            Event.objects.filter(deleted__isnull=False)
        )
        header = {"csrftoken": self.csrf_token}

        for already_deleted_event in already_deleted_events_queryset:
            # When
            response = self.client.delete(
                reverse('schedule:event_api', kwargs={"id": already_deleted_event.id}), **header)

            # Then
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
            self.assertEqual(response.json()['message'], '이미 삭제된 데이터 입니다.')

    def test_already_ended_event_request(self):
        # Given
        already_ended_event = Event.objects.create(
            title='이미 종료된 이벤트',
            description='종료되서 삭제되면 안되는 이벤트 ended_at은 현재날짜로부터 이미 1일이 지난 날짜로 설정',
            start_at=timezone.localtime() - timezone.timedelta(days=2),
            end_at=timezone.localtime() - timezone.timedelta(days=1),
            author='KimSoungRyoul',
            category='사내',
        )
        header = {"csrftoken": self.csrf_token}

        # When
        response = self.client.delete(
            reverse('schedule:event_api', kwargs={"id": already_ended_event.id}), **header)

        # Then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json()['message'], '일정이 종료된 데이터는 삭제할수 없습니다.')
