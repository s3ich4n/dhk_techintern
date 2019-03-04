from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from schedule.exceptions import AccessAlreadyEndedEventException
from schedule.models import Event
from schedule.tests.utils import AssertNotRaise


class EventModelMethodTest(TestCase, AssertNotRaise):
    def setUp(self):
        username = 'root'
        password = 'django_password'
        User.objects.filter(username=username).delete()
        User.objects.create_superuser(username=username, password=password, email='')
        self.client.login(username='root', password='django_password')

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

    def test_get_not_ended_event_should_raise_does_not_exist_when_taking_nonexistent_event_id(self):
        # Given
        to_be_deleted_event = self.create_event_with_event_time(timezone.now())
        Event.objects.filter(id=to_be_deleted_event.id).delete()
        nonexistent_event_id = to_be_deleted_event.id
        found_event = None

        # When
        with self.assertRaises(Event.DoesNotExist) as cm:
            found_event = Event.get_not_ended_event(
                event_id=nonexistent_event_id,
                present_time=timezone.now(),
            )

        # Then
        self.assertIsInstance(cm.exception, Event.DoesNotExist)
        self.assertIsNone(found_event)

    def test_get_not_ended_event_should_raise_access_already_ended_event_exception_when_present_later_than_end_time(
            self):
        # Given
        present_time = timezone.now()
        # 현재시간을 기준으로 이미 종료된 이벤트 id.
        already_ended_event_id = self.create_event_with_event_time(
            event_time=present_time - timedelta(seconds=1),
        ).id
        found_event = None

        # When
        # 이미 종료된 이벤트는 수정의 대상이 아니므로
        # 수정 폼에 들어갈 이벤트 객체를 가져오려고 할 경우 AccessAlreadyEndedException이 발생해야 함.
        with self.assertRaises(AccessAlreadyEndedEventException) as cm:
            found_event = Event.get_not_ended_event(
                event_id=already_ended_event_id,
                present_time=present_time,
            )

        # Then
        self.assertIsInstance(cm.exception, AccessAlreadyEndedEventException)
        self.assertIsNone(found_event)

    def test_get_not_ended_event_should_raise_access_already_ended_event_exception_when_present_same_with_end_time(
            self):
        # Given
        present_time = timezone.now()
        # 현재시간과 동일한 이벤트 종료시간을 갖는 이벤트 id.
        present_end_time_event_id = self.create_event_with_event_time(
            event_time=present_time,
        ).id
        found_event = None

        # When
        # 현재시간과 동일한 종료시간을 갖는 이벤트는 수정의 대상이 아니므로
        # 수정 폼에 들어갈 이벤트 객체를 가져오려고 할 경우 AccessAlreadyEndedEventException이 발생해야 함.
        with self.assertRaises(AccessAlreadyEndedEventException) as cm:
            found_event = Event.get_not_ended_event(
                event_id=present_end_time_event_id,
                present_time=present_time,
            )

        # Then
        self.assertIsInstance(cm.exception, AccessAlreadyEndedEventException)
        self.assertIsNone(found_event)

    def test_get_not_ended_event_should_not_raise_does_not_exist_when_present_time_is_earlier_than_end_time(self):
        # Given
        present_time = timezone.now()
        # 현재시간을 기준으로 아직 종료되지 않은 이벤트 id.
        not_ended_event_id = self.create_event_with_event_time(
            event_time=present_time + timedelta(seconds=1)
        ).id
        found_event = None

        # When
        # 현재시간을 기준으로 아직 종료되지 않은 이벤트는 수정의 대상에 속하므로
        # 수정 폼에 들어갈 이벤트 객체를 가져오려고 할 경우 Event.DoesNotExists 예외가 발생하지 않아야 함.
        with self.assertNotRaises(Event.DoesNotExist) as exp:
            found_event = Event.get_not_ended_event(
                event_id=not_ended_event_id,
                present_time=present_time
            )

        # Then
        self.assertNotIsInstance(exp, Event.DoesNotExist)
        self.assertIsInstance(found_event, Event)

    def test_get_not_ended_event_should_not_raise_access_already_ended_event_exception_when_present_earlier_than_end_time(
            self):
        # Given
        present_time = timezone.now()
        # 현재시간을 기준으로 아직 종료되지 않은 이벤트 id.
        not_ended_event_id = self.create_event_with_event_time(
            event_time=present_time + timedelta(seconds=1)
        ).id
        found_event = None

        # When
        # 현재시간을 기준으로 아직 종료되지 않은 이벤트는 수정의 대상에 속하므로
        # 수정 폼에 들어갈 이벤트 객체를 가져오려고 할 경우 AccessAlreadyEndedEventException 예외가 발생하지 않아야 함.
        with self.assertNotRaises(AccessAlreadyEndedEventException) as exp:
            found_event = Event.get_not_ended_event(
                event_id=not_ended_event_id,
                present_time=present_time
            )

        # Then
        self.assertNotIsInstance(exp, AccessAlreadyEndedEventException)
        self.assertIsInstance(found_event, Event)
