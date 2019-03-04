from datetime import timedelta, datetime
from http import HTTPStatus

from django.contrib.auth.models import User
from django.http import HttpResponseNotFound, HttpResponseForbidden, JsonResponse
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from schedule.models import Event


class EventUpdateViewTest(TestCase):
    '''
    이벤트 종료시간이 현재시간보다 이르거나 같을 경우에는 수정이 불가능.
    진행중이거나 진행예정인 이벤트만 수정 가능.
    '''

    def setUp(self):
        username = 'root'
        password = 'django_password'
        User.objects.filter(username=username).delete()
        User.objects.create_superuser(username=username, password=password, email='')
        self.client.login(username='root', password='django_password')

        self.forbidden_message = '접근할 수 없는 이벤트입니다.'
        self.url = 'schedule:update-event'

    @staticmethod
    def create_event_with_event_time(event_time=None):
        '''
        :param event_time: start_at, end_at에 들어갈 값.
        :return: 테스트케이스에 필요한 이벤트 데이터.
        '''
        if event_time is None:
            event_time = timezone.now()
        return Event.objects.create(
            title='타이틀',
            category='사내',
            start_at=event_time,
            end_at=event_time,
            author='kde6260',
        )

    @staticmethod
    def convert_event_object_as_dict(event):
        event_as_dictionary = {
            'title': event.title,
            'category': event.category,
            'start_at': event.start_at,
            'end_at': event.end_at,
            'description': event.description,
            'author': event.author
        }
        return event_as_dictionary

    def test_put_method_should_return_not_found_when_requesting_to_update_nonexistent_event(self):
        # Given
        # 존재하지 않는 이벤트의 id
        to_be_deleted_event = self.create_event_with_event_time(timezone.now())
        Event.objects.filter(id=to_be_deleted_event.id).delete()
        nonexistent_event_id = to_be_deleted_event.id

        # When
        # 존재하지 않는 이벤트의 id로 http 요청.
        response = self.client.put(
            path=reverse(self.url, kwargs={
                'id': nonexistent_event_id,
            }),
            data={},
            content_type='application/json;charset=utf-8;'
        )

        # Then
        # 없는 이벤트의 id로 요청했으므로 Not Found로 응답해야 함.
        self.assertIsInstance(response, HttpResponseNotFound)
        self.assertContains(
            response=response,
            text='Not Found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    def test_put_method_should_return_forbidden_when_requesting_to_update_event_end_time_earlier_than_present(self):
        # Given
        present_time = timezone.now()
        already_ended_event = self.create_event_with_event_time(
            event_time=present_time - timedelta(seconds=1),
        )

        # When
        # 이미 종료된 이벤트의 수정을 요청.
        response = self.client.put(
            path=reverse(self.url, kwargs={
                'id': already_ended_event.id,
            }),
            data=self.convert_event_object_as_dict(already_ended_event),
            content_type='application/json;charset=utf-8;'
        )

        # Then
        # 이미 종료된 이벤트의 수정을 요청했으므로 Forbidden으로 응답해야 함.
        self.assertIsInstance(response, HttpResponseForbidden)
        self.assertContains(
            response=response,
            text=self.forbidden_message,
            status_code=HTTPStatus.FORBIDDEN,
        )

    def test_put_method_should_return_forbidden_when_requesting_to_update_event_end_time_same_with_present(self):
        # Given
        present_time = timezone.now()
        event_with_end_time_same_with_present_time = self.create_event_with_event_time(
            event_time=present_time,
        )

        # When
        # 종료시간이 현재시간과 동일한 이벤트의 수정을 요청.
        response = self.client.put(
            path=reverse(self.url, kwargs={
                'id': event_with_end_time_same_with_present_time.id,
            }),
            data=self.convert_event_object_as_dict(event_with_end_time_same_with_present_time),
            content_type='application/json;charset=utf-8;'
        )

        # Then
        # 종료시간이 현재시간과 동일한 이벤트의 수정을 요청했으므로 Forbidden으로 응답해야 함.
        self.assertIsInstance(response, HttpResponseForbidden)
        self.assertContains(
            response=response,
            text=self.forbidden_message,
            status_code=HTTPStatus.FORBIDDEN,
        )

    def test_put_method_should_return_updated_event_id_when_requesting_to_update_not_ended_event(self):
        # Given
        present_time = timezone.now()
        not_ended_event = self.create_event_with_event_time(
            event_time=present_time + timedelta(seconds=1),
        )
        time_format = '%Y-%m-%d %H:%M:%S'
        changed_time = datetime(2018, 11, 9, 12, 30)
        changed_time_in_utc = changed_time - timedelta(hours=9)

        # When
        # 아직 종료되지 않은 이벤트의 수정을 요청.
        response = self.client.put(
            path=reverse(self.url, kwargs={
                'id': not_ended_event.id,
            }),
            data={
                'title': '수정된 타이틀',
                'category': '사외',
                'start_at': changed_time.strftime(time_format),
                'end_at': changed_time.strftime(time_format),
                'description': '수정된 상세설명',
                'author': 'kde6260'
            },
            content_type='application/json;charset=utf-8;'
        )
        updated_event = Event.objects.get(id=not_ended_event.id)

        # Then
        self.assertIsInstance(response, JsonResponse)

        # 수정된 이벤트의 각 필드의 값은 수정 요청한 필드의 값과 같아야 함.
        self.assertEqual(updated_event.title, '수정된 타이틀')
        self.assertEqual(updated_event.category, '사외')
        self.assertEqual(updated_event.start_at.strftime(time_format), changed_time_in_utc.strftime(time_format))
        self.assertEqual(updated_event.end_at.strftime(time_format), changed_time_in_utc.strftime(time_format))
        self.assertEqual(updated_event.description, '수정된 상세설명')
        self.assertEqual(updated_event.author, 'kde6260')
