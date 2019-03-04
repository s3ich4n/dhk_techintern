import json
from copy import deepcopy
from datetime import datetime, timedelta
from http import HTTPStatus

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import model_to_dict
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from schedule.models import Event
from schedule.views import api_retrieve_all_month_data


class EventCreateViewTests(TestCase):
    fixtures = ['event.json', ]

    @classmethod
    def setUpClass(cls):
        super(EventCreateViewTests, cls).setUpClass()
        cls.path = reverse('schedule:api-retrieve-monthly-value')
        cls.factory = RequestFactory()
        cls.start_at_allday_time = datetime.strptime('00:00', '%H:%M').time()
        cls.start_at_default_time = datetime.strptime('17:00', '%H:%M').time()
        cls.end_at_default_time = datetime.strptime('00:00', '%H:%M').time()

    def setUp(self):
        username = 'root'
        password = 'django_password'
        User.objects.filter(username=username).delete()
        User.objects.create_superuser(username=username, password=password, email='')
        self.client.login(username='root', password='django_password')

        self.sample_data = {
            'title': 'test_title',
            'category': '사내',
            'author': 'test_author',
            'description': 'test_desc',
            'start_at': "2018-11-11 17:00",
            'end_at': "2018-11-11 22:00",
            'start_at_type': 'datetime',
            'end_at_type': 'datetime',
            'is_allday': False,
        }

    @staticmethod
    def convert_datetime_to_iso_format_string(model_instance):
        model_instance_copied = deepcopy(model_instance)
        model_instance_copied.start_at = model_instance.start_at.astimezone().isoformat()
        model_instance_copied.end_at = model_instance.end_at.astimezone().isoformat()
        return model_instance_copied

    def generate_request(self, data, method):
        request = method(
            self.path,
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        return request

    def test_response_status_is_created_and_db_data_equals_to_response_json_for_same_fields_when_data_is_valid(self):
        # Given
        data = self.sample_data

        # When
        request = self.generate_request(data, self.factory.post)
        response = api_retrieve_all_month_data.RetrieveMonthlyEvent.post(request)
        response_json = json.loads(response.content)
        model_instance = Event.objects.get(id=response_json.get('id'))
        model_instance_converted = self.convert_datetime_to_iso_format_string(model_instance)
        db_data = model_to_dict(model_instance_converted, fields=response_json.keys())

        # Then
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertDictEqual(response_json, db_data)

    def test_response_status_is_created_and_start_at_time_is_17_when_start_at_has_only_date(self):
        # Given
        data = self.sample_data
        data['start_at'] = '2018-11-01'
        data['start_at_type'] = 'date'

        # When
        request = self.generate_request(data, self.factory.post)
        response = api_retrieve_all_month_data.RetrieveMonthlyEvent.post(request)
        response_json = json.loads(response.content)
        model_instance = Event.objects.get(id=response_json.get('id'))
        model_instance_converted = self.convert_datetime_to_iso_format_string(model_instance)
        db_data = model_to_dict(model_instance_converted, fields=response_json.keys())

        # Then
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertDictEqual(response_json, db_data)
        self.assertEqual(model_instance.start_at.astimezone().time(), self.start_at_default_time)

    def test_response_status_is_created_and_start_at_equals_to_end_at_when_end_at_is_not_inserted(self):
        # Given
        data = self.sample_data
        data['end_at'] = ''
        data['end_at_type'] = ''

        # When
        request = self.generate_request(data, self.factory.post)
        response = api_retrieve_all_month_data.RetrieveMonthlyEvent.post(request)
        response_json = json.loads(response.content)
        model_instance = Event.objects.get(id=response_json.get('id'))
        model_instance_converted = self.convert_datetime_to_iso_format_string(model_instance)
        db_data = model_to_dict(model_instance_converted, fields=response_json.keys())

        # Then
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertDictEqual(response_json, db_data)
        self.assertEqual(db_data['start_at'], db_data['end_at'])

    def test_response_status_is_created_and_end_at_is_12am_of_next_day_when_end_at_has_only_date(self):
        # Given
        data = self.sample_data
        data['end_at'] = '2018-12-01'
        data['end_at_type'] = 'date'
        end_at_date = datetime.strptime(data['end_at'], '%Y-%m-%d').date() + timedelta(days=1)

        # When
        request = self.generate_request(data, self.factory.post)
        response = api_retrieve_all_month_data.RetrieveMonthlyEvent.post(request)
        response_json = json.loads(response.content)
        model_instance = Event.objects.get(id=response_json.get('id'))
        model_instance_converted = self.convert_datetime_to_iso_format_string(model_instance)
        db_data = model_to_dict(model_instance_converted, fields=response_json.keys())

        # Then
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertDictEqual(response_json, db_data)
        self.assertEqual(model_instance.end_at.astimezone().date(), end_at_date)
        self.assertEqual(model_instance.end_at.astimezone().time(), self.end_at_default_time)

    def test_response_status_is_created_and_end_at_date_has_start_at_date_when_end_at_has_only_time(self):
        # Given
        data = self.sample_data
        data['end_at'] = '23:00'
        data['end_at_type'] = 'time'

        # When
        request = self.generate_request(data, self.factory.post)
        response = api_retrieve_all_month_data.RetrieveMonthlyEvent.post(request)
        response_json = json.loads(response.content)
        model_instance = Event.objects.get(id=response_json.get('id'))
        model_instance_converted = self.convert_datetime_to_iso_format_string(model_instance)
        db_data = model_to_dict(model_instance_converted, fields=response_json.keys())

        # Then
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertDictEqual(response_json, db_data)
        self.assertEqual(model_instance.end_at.astimezone().date(), model_instance.start_at.astimezone().date())

    def test_event_form_should_valid_and_start_end_time_is_12am_and_end_at_date_is_next_day_when_all_day_is_set(self):
        # Given
        all_day_set_data = self.sample_data
        all_day_set_data['is_allday'] = 'true'
        start_at = datetime.strptime(all_day_set_data['start_at'], '%Y-%m-%d %H:%M')
        end_at = datetime.strptime(all_day_set_data['end_at'], '%Y-%m-%d %H:%M')

        # When
        request = self.generate_request(all_day_set_data, self.factory.post)
        response = api_retrieve_all_month_data.RetrieveMonthlyEvent.post(request)
        response_json = json.loads(response.content)
        model_instance = Event.objects.get(id=response_json.get('id'))
        model_instance_converted = self.convert_datetime_to_iso_format_string(model_instance)
        db_data = model_to_dict(model_instance_converted, fields=response_json.keys())

        # Then
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertDictEqual(response_json, db_data)
        self.assertEqual(model_instance.start_at.astimezone().date(), start_at.date())
        self.assertEqual(model_instance.start_at.astimezone().time(), self.start_at_allday_time)
        self.assertEqual(model_instance.end_at.astimezone().date(), end_at.date() + timedelta(days=1))
        self.assertEqual(model_instance.end_at.astimezone().time(), self.end_at_default_time)

    def test_response_status_is_bad_request_and_event_does_not_exist_when_title_is_not_inserted(self):
        # Given
        invalid_data = self.sample_data
        invalid_data['title'] = ''

        # When
        request = self.generate_request(invalid_data, self.factory.post)
        response = api_retrieve_all_month_data.RetrieveMonthlyEvent.post(request)
        response_json = json.loads(response.content)

        # Then
        self.assertContains(response, 'title', status_code=HTTPStatus.BAD_REQUEST)
        self.assertIsNone(response_json.get('id'))
        self.assertFalse(Event.objects.filter(title=invalid_data['title']).exists())

    def test_response_status_is_bad_request_and_event_does_not_exist_when_author_is_not_inserted(self):
        # Given
        invalid_data = self.sample_data
        invalid_data['author'] = ''

        # When
        request = self.generate_request(invalid_data, self.factory.post)
        response = api_retrieve_all_month_data.RetrieveMonthlyEvent.post(request)
        response_json = json.loads(response.content)

        # Then
        self.assertContains(response, 'author', status_code=HTTPStatus.BAD_REQUEST)
        self.assertIsNone(response_json.get('id'))
        self.assertFalse(Event.objects.filter(author=invalid_data['author']).exists())

    def test_response_status_is_bad_request_and_occurs_validation_error_when_start_at_is_not_valid(self):
        invalid_params = ['', '17:00']
        invalid_type = ['', 'time']
        invalid_data = self.sample_data

        for param, type_ in zip(invalid_params, invalid_type):
            # Given
            invalid_data['start_at'] = param
            invalid_data['start_at_type'] = type_

            # When
            request = self.generate_request(invalid_data, self.factory.post)
            response = api_retrieve_all_month_data.RetrieveMonthlyEvent.post(request)
            response_json = json.loads(response.content)

            # Then
            self.assertContains(response, 'start_at', status_code=HTTPStatus.BAD_REQUEST)
            self.assertIsNone(response_json.get('id'))
            with self.assertRaises(ValidationError):
                Event.objects.filter(start_at=invalid_data['start_at'])

    def test_response_status_is_bad_request_and_occurs_validation_error_when_start_at_and_end_at_is_not_inserted(self):
        # Given
        invalid_data = self.sample_data
        invalid_data['start_at'], invalid_data['start_at_type'] = '', ''
        invalid_data['end_at'], invalid_data['end_at_type'] = '', ''

        # When
        request = self.generate_request(invalid_data, self.factory.post)
        response = api_retrieve_all_month_data.RetrieveMonthlyEvent.post(request)
        response_json = json.loads(response.content)

        # Then
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIsNone(response_json.get('id'))
        with self.assertRaises(ValidationError):
            Event.objects.filter(start_at=invalid_data['start_at'], end_at=invalid_data['end_at'])

    def test_response_status_is_bad_request_and_event_does_not_exist_when_end_at_is_earlier_than_start_at(self):
        # Given
        invalid_data = self.sample_data
        start_at = datetime.strptime(invalid_data['start_at'], '%Y-%m-%d %H:%M')
        earlier_time = start_at - timedelta(minutes=1)
        invalid_data['end_at'] = earlier_time.strftime('%Y-%m-%d %H:%M')

        # When
        request = self.generate_request(invalid_data, self.factory.post)
        response = api_retrieve_all_month_data.RetrieveMonthlyEvent.post(request)
        response_json = json.loads(response.content)

        # Then
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIsNone(response_json.get('id'))
        self.assertFalse(Event.objects.filter(
            start_at=timezone.make_aware(datetime.strptime(invalid_data['start_at'], '%Y-%m-%d %H:%M')),
            end_at=timezone.make_aware(datetime.strptime(invalid_data['end_at'], '%Y-%m-%d %H:%M'))))
