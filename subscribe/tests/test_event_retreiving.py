from datetime import timedelta, time

from django.test import TestCase
from django.utils import timezone

from schedule.models import Event
from subscribe.scripts.mail_sender import retrieve_list_of_events

'''
당일에 있는 이벤트를 전송한다.
'''


class TestEventRetrieving(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestEventRetrieving, cls).setUpClass()

        cls.today = timezone.now()

        cls.start_in_date = timezone.now()
        cls.end_in_date = timezone.now()

        cls.start_out_of_date = timezone.now() - timedelta(days=1)
        cls.end_out_of_date = timezone.now() + timedelta(days=1)

    def test_date_out_of_range_should_not_send_email(self):
        # GIVEN
        start_event_out_of_range = Event.objects.create(  # noqa
            title='start_at out of bound events',
            start_at=self.start_out_of_date,
            end_at=self.today,
        )
        end_event_out_of_range = Event.objects.create(  # noqa
            title='end_at out of bound events',
            start_at=self.today,
            end_at=self.end_out_of_date,
        )

        # WHEN
        start_event_empty_qset = retrieve_list_of_events()
        end_event_empty_qset = retrieve_list_of_events()

        # THEN
        self.assertQuerysetEqual(start_event_empty_qset, Event.objects.none())
        self.assertQuerysetEqual(end_event_empty_qset, Event.objects.none())

    def test_event_both_of_it_should_send_email(self):
        # GIVEN
        self.start_in_date = timezone.make_aware(self.start_in_date.combine(self.start_in_date, time.max))
        self.end_in_date = timezone.make_aware(self.end_in_date.combine(self.end_in_date, time.max))

        both_range_in_boundary = Event.objects.create(  # noqa
            title='start in boundary',
            start_at=self.start_in_date,
            end_at=self.end_in_date
        )

        # WHEN
        both_range_in_boundary_list = retrieve_list_of_events()

        # THEN
        self.assertEqual(1, both_range_in_boundary_list.count())
