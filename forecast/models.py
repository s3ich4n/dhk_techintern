from django.db import models
from django.utils import timezone


class Forecast(models.Model):
    date = models.DateField(
        help_text='캘린더에서 제공하는 날짜',
    )
    region = models.ForeignKey(
        'Region',
        on_delete=models.CASCADE,
    )
    temperature = models.FloatField(
        null=True,
        help_text='해당 날짜+지역의 기온.',
    )
    weather = models.TextField(
        help_text='해당 날짜+지역의 날씨상태.'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        help_text='예보가 새로 생성된 시간',
    )
    updated = models.DateTimeField(
        auto_now=True,
        help_text='예보가 수정된 시간',
    )

    class Meta:
        unique_together = (
            ('date', 'region'),
        )

    def __init__(self, *args, **kwargs):
        if not kwargs.get('date'):
            kwargs['date'] = timezone.now().strftime('%Y-%m-%d')
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'(date:{self.date}, temp:{self.temperature}, weather:{self.weather}, region_name:{self.region.name})'


class Region(models.Model):
    name = models.CharField(
        unique=True,
        max_length=10,
        help_text='지역 이름',
    )
    latitude = models.FloatField(
        help_text='위도',
    )
    longitude = models.FloatField(
        help_text='경도',
    )
    observing_station = models.PositiveSmallIntegerField(
        help_text='지역별 관측소 번호',
    )

    def __repr__(self):
        return self.name
