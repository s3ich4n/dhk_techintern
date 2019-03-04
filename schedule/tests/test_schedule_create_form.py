from datetime import datetime, timedelta

from django.test import TestCase

from schedule.forms import EventForm


class EventCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(EventCreateFormTests, cls).setUpClass()
        cls.event_required_keys = [
            'title',
            'category',
            'author',
            'description',
            'start_at',
            'end_at',
            'is_allday',
        ]
        cls.start_at_allday_time = datetime.strptime('00:00', '%H:%M').time()
        cls.start_at_default_time = datetime.strptime('17:00', '%H:%M').time()
        cls.end_at_default_time = datetime.strptime('00:00', '%H:%M').time()

    def setUp(self):
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

    def test_event_form_should_valid_and_does_not_have_errors_and_all_fields_are_not_none_when_data_is_valid(self):
        # Given
        data = self.sample_data

        # When
        form = EventForm(data=data)

        # Then
        self.assertFalse(form.errors)
        self.assertTrue(form.is_valid())
        for key in self.event_required_keys:
            self.assertIsNotNone(form.cleaned_data.get(key))

    def test_event_form_should_valid_and_start_at_time_is_17_when_start_at_has_only_date(self):
        # Given
        data = self.sample_data
        data['start_at'] = '2018-11-01'
        data['start_at_type'] = 'date'

        # When
        form = EventForm(data=data)

        # Then
        self.assertFalse(form.errors)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_at'].astimezone().time(), self.start_at_default_time)

    def test_event_form_should_valid_and_start_at_equals_to_end_at_when_end_at_is_not_inserted(self):
        # Given
        data = self.sample_data
        data['end_at'] = ''
        data['end_at_type'] = ''

        # When
        form = EventForm(data=data)

        # Then
        self.assertFalse(form.errors)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_at'], form.cleaned_data['end_at'])

    def test_event_form_should_valid_and_end_at_is_12am_of_next_day_when_end_at_has_only_date(self):
        # Given
        data = self.sample_data
        data['end_at'] = '2018-12-01'
        data['end_at_type'] = 'date'
        end_at_date = datetime.strptime(data['end_at'], '%Y-%m-%d').date() + timedelta(days=1)

        # When
        form = EventForm(data=data)

        # Then
        self.assertFalse(form.errors)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['end_at'].astimezone().date(), end_at_date)
        self.assertEqual(form.cleaned_data['end_at'].astimezone().time(), self.end_at_default_time)

    def test_event_form_should_valid_and_end_at_date_is_start_at_date_when_end_at_has_only_time(self):
        # Given
        data = self.sample_data
        data['end_at'] = '23:00'
        data['end_at_type'] = 'time'

        # When
        form = EventForm(data=data)

        # Then
        self.assertFalse(form.errors)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['end_at'].date(), form.cleaned_data['start_at'].date())

    def test_event_form_should_valid_and_start_end_time_is_12am_and_end_at_date_is_next_day_when_all_day_is_set(self):
        # Given
        all_day_set_data = self.sample_data
        all_day_set_data['is_allday'] = True
        start_at_before_clean = datetime.strptime(all_day_set_data['start_at'], '%Y-%m-%d %H:%M')
        end_at_before_clean = datetime.strptime(all_day_set_data['end_at'], '%Y-%m-%d %H:%M')

        # When
        form = EventForm(data=all_day_set_data)

        # Then
        self.assertFalse(form.errors)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_at'].date(), start_at_before_clean.date())
        self.assertEqual(form.cleaned_data['start_at'].astimezone().time(), self.start_at_allday_time)
        self.assertEqual(form.cleaned_data['end_at'].date(), end_at_before_clean.date() + timedelta(days=1))
        self.assertEqual(form.cleaned_data['end_at'].astimezone().time(), self.end_at_default_time)
        for key in self.event_required_keys:
            self.assertIsNotNone(form.cleaned_data.get(key))

    def test_event_form_should_not_valid_and_cleaned_title_does_not_exist_when_title_is_not_inserted(self):
        # Given
        invalid_data = self.sample_data
        invalid_data['title'] = ''

        # When
        form = EventForm(data=invalid_data)

        # Then
        self.assertTrue(form.errors['title'])
        self.assertFalse(form.is_valid())
        self.assertIsNone(form.cleaned_data.get('title'))

    def test_event_form_should_not_valid_and_cleaned_author_does_not_exist_when_author_is_not_inserted(self):
        # Given
        invalid_data = self.sample_data
        invalid_data['author'] = ''

        # When
        form = EventForm(data=invalid_data)

        # Then
        self.assertTrue(form.errors['author'])
        self.assertFalse(form.is_valid())
        self.assertIsNone(form.cleaned_data.get('author'))

    def test_event_form_should_not_valid_and_cleaned_start_at_is_none_when_start_at_is_not_valid(self):
        invalid_params = ['', '17:00']
        invalid_type = ['', 'time']
        invalid_data = self.sample_data

        for param, type_ in zip(invalid_params, invalid_type):
            # Given
            invalid_data['start_at'] = param
            invalid_data['start_at_type'] = type_

            # When
            form = EventForm(data=invalid_data)

            # Then
            self.assertFalse(form.is_valid())
            self.assertTrue(form.errors['start_at'])
            self.assertIsNone(form.cleaned_data.get('start_at'))

    def test_event_form_should_not_valid_and_cleaned_data_are_none_when_start_at_and_end_at_are_not_inserted(self):
        # Given
        invalid_data = self.sample_data
        invalid_data['start_at'], invalid_data['start_at_type'] = '', ''
        invalid_data['end_at'], invalid_data['end_at_type'] = '', ''

        # When
        form = EventForm(data=invalid_data)

        # Then
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors['start_at'])
        self.assertTrue(form.errors['end_at'])
        self.assertIsNone(form.cleaned_data.get('start_at'))
        self.assertIsNone(form.cleaned_data.get('end_at'))

    def test_event_form_should_not_valid_and_has_non_field_error_when_end_at_is_earlier_than_start_at(self):
        # Given
        invalid_data = self.sample_data
        start_at = datetime.strptime(invalid_data['start_at'], '%Y-%m-%d %H:%M')
        earlier_time = start_at - timedelta(minutes=1)
        invalid_data['end_at'] = earlier_time.strftime('%Y-%m-%d %H:%M')

        # When
        form = EventForm(data=invalid_data)

        # Then
        self.assertTrue(form.errors['__all__'])
        self.assertFalse(form.is_valid())
        self.assertGreater(form.cleaned_data['start_at'], form.cleaned_data['end_at'])
