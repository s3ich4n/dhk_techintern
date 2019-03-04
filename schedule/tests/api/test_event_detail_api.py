from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from schedule.models import Event


class EventDetailAPITest(TestCase):
    fixtures = ['event.json', 'user.json', ]

    def setUp(self):
        self.client.login(username='root', password='django_password')

    def test_request_normal(self):
        # Given
        for event_id_in_event_dummy_data in Event.objects.filter(deleted__isnull=True):
            # When
            response = self.client.get(
                reverse('schedule:event_api', kwargs={"id": event_id_in_event_dummy_data.id}))

            # Then
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIsNotNone(response.json()['title'])

    def test_request_deleted_event(self):
        # Given
        deleted_event_id = Event.objects.get(deleted__isnull=False).id

        # When
        response = self.client.get(reverse('schedule:event_api', kwargs={"id": deleted_event_id}))

        # Then
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_request_no_exist_event(self):
        # Given
        deleted_event_id = Event.objects.get(deleted__isnull=False).id
        Event.objects.filter(id=deleted_event_id).update(deleted=timezone.now())

        # When
        response = self.client.get(reverse('schedule:event_api', kwargs={"id": deleted_event_id}))

        # Then
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.json()['message'], '해당 id 값의 이벤트가 존재하지 않습니다.')
