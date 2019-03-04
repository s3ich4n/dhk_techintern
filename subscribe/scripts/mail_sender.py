from datetime import timedelta, time, datetime

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import get_template
from django.utils import timezone

from schedule.models import Event

User = get_user_model()

A_DAY = timedelta(days=1)


# 0 10 * * 1-5 /holiday_desc.sh
def send_mail_for_subscriber():
    recipient_from_db = User.objects.filter(subscriber_of__is_subscribed=True).values('email')
    recipient_list = [mail['email'] for mail in recipient_from_db]

    data = retrieve_list_of_events()

    if not data:
        return

    else:
        subjects = [d['title'] for d in data]
        descriptions = [d['description'] for d in data]

        email_subject = f'[AlertYo] 오늘의 예정된 이벤트는 {data.count()}건 입니다.'
        email_text = []
        for subject, message in zip(subjects, descriptions):
            email_text.append(f'{subject}: {message}\n')

        send_mail(
            email_subject,
            '',
            settings.EMAIL_HOST_USER,
            recipient_list,
            html_message=get_template('email/email_template.html').render(
                {
                    'email_text': email_text,
                    'server_url': settings.SERVER_URL,
                }
            ),
        )


def retrieve_list_of_events():
    """
    KST기준, 오늘의 이벤트를 모두 가져온다.
    :return: None or QuerySet
    """

    kst_tz = pytz.timezone(settings.TIME_ZONE)
    now = timezone.now().astimezone(tz=kst_tz)
    today_min = timezone.make_aware(datetime.combine(now, time.min))
    today_max = timezone.make_aware(datetime.combine(now, time.max))

    return (Event.objects
            .filter(Q(deleted__isnull=True)
                    & Q(start_at__range=(today_min, today_max))
                    & Q(end_at__range=(today_min, today_max)))
            .values('title', 'description', 'start_at', 'end_at'))
