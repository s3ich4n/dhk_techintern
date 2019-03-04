import datetime

from django.db import models
from django.utils import timezone

from schedule.exceptions import AccessAlreadyEndedEventException


class RetrieveEventQuerySet(models.QuerySet):
    def __query_range_events(self, start_date, end_date):
        return self.filter(
            start_at__range=[start_date, end_date],
            end_at__range=[start_date, end_date],
            deleted__isnull=True,
        ).values(
            'id', 'title', 'category',
            'start_at', 'end_at', 'description',
            'author', 'is_allday',
        )

    def monthly_events(self, start_date, end_date):
        return self.__query_range_events(start_date, end_date)

    def daily_events(self, start_date, end_date, target_date):
        return self.filter(
            start_at__range=(start_date, target_date + datetime.timedelta(1)),
            end_at__range=(target_date, end_date),
            deleted__isnull=True,
        ).values(
            'id', 'title', 'category',
            'start_at', 'end_at', 'description',
            'author', 'is_allday',
        )


class RetrieveEventManager(models.Manager):
    def get_queryset(self):
        return RetrieveEventQuerySet(self.model, using=self._db)

    def monthly_event(self, start_date, end_date):
        return self.get_queryset().monthly_events(
            start_date, end_date
        )

    def daily_event(self, start_date, end_date, target_date):
        return self.get_queryset().daily_events(
            start_date, end_date, target_date
        )


class TimeStampedModel(models.Model, RetrieveEventManager):
    deleted = models.DateTimeField(
        help_text='삭제된 시간',
        null=True,
    )

    created = models.DateTimeField(
        help_text='생성 날짜 기록',
        auto_now_add=True
    )

    updated = models.DateTimeField(
        help_text='변경 날짜 기록',
        auto_now=True
    )

    date_related_objects = RetrieveEventManager()
    objects = models.Manager()

    class Meta:
        abstract = True


class Event(TimeStampedModel):
    """
    사내/사외 이벤트 공통항목
    """

    title = models.CharField(
        help_text='이벤트 제목',
        max_length=100,
    )

    category = models.CharField(
        help_text='이벤트 타입(사내/외로 구분)',
        max_length=50,
    )

    start_at = models.DateTimeField(
        # 기간이 아닌 시점에 이벤트를 할 때는 started_at에 기입.
        help_text='이벤트 시작 시점',
    )

    end_at = models.DateTimeField(
        # 특정 날짜만 기입하거나 미정일 경우를 고려해서 null=True
        help_text='이벤트 종료 시점',
    )

    description = models.CharField(
        help_text='이벤트에 대한 상세내용',
        max_length=300,
        blank=True,
        null=True,
    )

    author = models.CharField(
        help_text='작성자',
        max_length=50,
    )

    is_allday = models.BooleanField(
        help_text='하루 종일 이벤트 여부',
        default=False,
    )

    @property
    def is_ended_event(self):
        return self.end_at < timezone.now()

    @classmethod
    def get_not_ended_event(cls, event_id, present_time):
        try:
            event = cls.objects.get(id=event_id, deleted__isnull=True)
            if event.end_at <= present_time:
                raise AccessAlreadyEndedEventException()
            else:
                return event
        except cls.DoesNotExist as err:
            raise err
