from calendar import monthrange
from http import HTTPStatus
from datetime import date, datetime
from json import loads

from django.db.models import F
from django.test import TestCase
from django.urls import reverse

from forecast.common.constants import DATE_FORMAT
from forecast.models import Forecast, Region
from forecast.tests.common.classes import WeatherEnum, RegionEnum


def reshape_forecast_list_to_response_body(forecast_list_from_db, dates_from_db):
    content = []
    forecast_dict = {}
    if dates_from_db:
        for date_ in dates_from_db:
            date_string = date_['date'].strftime(DATE_FORMAT)
            content.append({
                'date': date_string,
            })
            forecast_dict.update({
                date_string: []
            })

    for f in forecast_list_from_db:
        formatted_date = f['date'].strftime(DATE_FORMAT)
        f['date'] = formatted_date
        f['weather'] = f['weather'].split('/')
        forecast_dict.get(formatted_date).append(f)

    for element in content:
        element.update({'forecasts': forecast_dict.get(element['date'])})

    return content


class TestGetForecastView(TestCase):
    fixtures = [
        'region.json',
        'forecast.json',
    ]

    @classmethod
    def setUpClass(cls):
        super(TestGetForecastView, cls).setUpClass()
        cls.maxDiff = None

        cls.this_year = 2018
        cls.this_month = 11
        cls.last_month = cls.this_month - 1

        Forecast.objects.create(
            temperature=30.1,
            weather=WeatherEnum.SUN.value,
            region=Region.objects.get(name=RegionEnum.SEOUL.value),
            date=date.today(),
        )
        Forecast.objects.create(
            temperature=30.1,
            weather=WeatherEnum.SUN.value,
            region=Region.objects.get(name=RegionEnum.DAEGU.value),
            date=date.today(),
        )

        Forecast.objects.create(
            temperature=30.1,
            weather=WeatherEnum.SUN.value,
            region=Region.objects.get(name=RegionEnum.DAEGEON.value),
            date=date.today(),
        )

        Forecast.objects.create(
            temperature=30.1,
            weather=WeatherEnum.SUN.value,
            region=Region.objects.get(name=RegionEnum.BUSAN.value),
            date=date.today(),
        )

    def test_get_forecasts_should_return_forecasts_between_start_and_end_when_start_end_are_valid(self):
        # start, end 파라미터에 유효한 값(둘 다 None이 아니고, 날짜포멧이며, start가 end보다 이른)이 들어올 경우
        # start와 end 사이에 있는 날짜를 date필드로 갖는 날씨정보로 응답해야 한다.
        # Given
        valid_start = datetime(self.this_year, self.this_month, 10)
        valid_end = datetime(self.this_year, self.this_month, 11)
        valid_querystring = {
            'start': valid_start.strftime(DATE_FORMAT),
            'end': valid_end.strftime(DATE_FORMAT),
        }
        expected_forecasts = reshape_forecast_list_to_response_body(
            forecast_list_from_db=list(Forecast.objects.filter(
                date__range=(valid_start.strftime(DATE_FORMAT), valid_end.strftime(DATE_FORMAT)),
            ).values(
                'date',
                'weather',
                'temperature',
                region_name=F('region__name'),
            )),
            dates_from_db=list(Forecast.objects.filter(
                date__range=(valid_start, valid_end)
            ).distinct('date').order_by('date').values('date')),
        )

        # When
        response = self.client.get(reverse('forecast:retrieve-forecasts'), data=valid_querystring)
        response_content = loads(response.content)

        # Then
        self.assertListEqual(response_content, expected_forecasts)

    def test_get_forecasts_should_return_forecast_of_this_month_when_start_end_is_none(self):
        # start, end 파라미터가 모두 None일 경우, 이번달의 날씨정보로 응답해야 한다.
        # Given
        today = date.today()
        this_month_1st_date = datetime(today.year, today.month, 1)
        this_month_last_date = datetime(today.year, today.month, monthrange(today.year, today.month)[1])
        expected_forecasts = reshape_forecast_list_to_response_body(
            forecast_list_from_db=list(Forecast.objects.filter(
                date__range=(
                    this_month_1st_date.strftime(DATE_FORMAT),
                    this_month_last_date.strftime(DATE_FORMAT)
                ),
            ).values(
                'date',
                'weather',
                'temperature',
                region_name=F('region__name'),
            )),
            dates_from_db=list(Forecast.objects.filter(
                date__range=(this_month_1st_date, this_month_last_date),
            ).distinct('date').order_by('date').values('date')),
        )

        # When
        response = self.client.get(reverse('forecast:retrieve-forecasts'), data=None)
        response_content = loads(response.content)

        # Then
        self.assertListEqual(response_content, expected_forecasts)

    def test_get_forecasts_should_return_bad_request_when_start_is_later_than_end(self):
        # start 파라미터가 end 파라미터보다 늦은 날짜로 들어올 경우 400으로 응답해야 한다.
        # Given
        later_start = datetime(self.this_year, self.this_month, 11)
        earlier_end = datetime(self.this_year, self.this_month, 10)

        # When
        response = self.client.get(reverse('forecast:retrieve-forecasts'), data={
            'start': later_start.strftime(DATE_FORMAT),
            'end': earlier_end.strftime(DATE_FORMAT),
        })

        # Then
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_get_forecasts_should_return_bad_request_when_start_end_are_not_date_format(self):
        # start, end 파라미터가 모두 날짜포멧이 아닌 값일 경우 400으로 응답해야 한다.
        # Given
        weird_format_start = 'some weird format.'
        weird_format_end = 'some weird format, too.'

        # When
        response = self.client.get(reverse('forecast:retrieve-forecasts'), data={
            'start': weird_format_start,
            'end': weird_format_end,
        })

        # Then
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_get_forecasts_should_return_bad_request_when_start_is_not_date_format(self):
        # start 파라미터가 날짜포멧이 아닌 값일 경우 400으로 응답해야 한다.
        # Given
        weird_format_start = 'some weird format.'
        valid_end = datetime(self.this_year, self.this_month, 10)

        # When
        response = self.client.get(reverse('forecast:retrieve-forecasts'), data={
            'start': weird_format_start,
            'end': valid_end.strftime(DATE_FORMAT),
        })

        # Then
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_get_forecasts_should_return_bad_request_when_end_is_not_date_format(self):
        # end 파라미터가 날짜포멧이 아닌 값일 경우 400으로 응답해야 한다.
        # Given
        valid_start = datetime(self.this_year, self.this_month, 10).strftime(DATE_FORMAT)
        weird_format_end = 'some weird format.'

        # When
        response = self.client.get(reverse('forecast:retrieve-forecasts'), data={
            'start': valid_start,
            'end': weird_format_end,
        })

        # Then
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_get_forecasts_should_return_forecasts_between_start_and_next_month_day_when_end_is_none(self):
        # end가 None일 경우 start와 다음 달 start의 일수에 해당하는 날짜의 날씨정보로 응답해야 한다.
        # 예) start = 2018-12-04 => end는 2019-01-04. start ~ end 사이의 date 필드를 갖는 날씨정보로 응답.
        # Given
        day = 10
        valid_start = datetime(self.this_year, self.last_month, day)
        replaced_end = datetime(self.this_year, self.last_month + 1, day)
        expected_forecasts = reshape_forecast_list_to_response_body(
            forecast_list_from_db=list(Forecast.objects.filter(
                date__range=(
                    valid_start.strftime(DATE_FORMAT),
                    replaced_end.strftime(DATE_FORMAT),
                ),
            ).values(
                'date',
                'weather',
                'temperature',
                region_name=F('region__name'),
            )),
            dates_from_db=list(Forecast.objects.filter(
                date__range=(valid_start, replaced_end)
            ).distinct('date').order_by('date').values('date')),
        )
        # When
        response = self.client.get(reverse('forecast:retrieve-forecasts'), data={
            'start': valid_start.strftime(DATE_FORMAT),
        })
        response_content = loads(response.content)

        # Then
        self.assertListEqual(response_content, expected_forecasts)

    def test_get_forecasts_should_return_forecasts_between_prev_month_day_and_end_when_start_is_none(self):
        # start가 None일 경우 end 기준 저번 달 ~ end의 일수에 해당하는 날짜의 날씨정보로 응답해야 한다.
        # 예) end = 2018-12-04 => start는 2018-11-04. start ~ end 사이의 date 필드를 갖는 날씨정보로 응답.
        # Given
        day = 10
        valid_end = datetime(self.this_year, self.this_month, day)
        replaced_start = datetime(self.this_year, self.this_month - 1, day)

        expected_forecasts = reshape_forecast_list_to_response_body(
            forecast_list_from_db=list(Forecast.objects.filter(
                date__range=(
                    replaced_start.strftime(DATE_FORMAT),
                    valid_end.strftime(DATE_FORMAT),
                ),
            ).values(
                'date',
                'weather',
                'temperature',
                region_name=F('region__name'),
            )),
            dates_from_db=list(Forecast.objects.filter(
                date__range=(replaced_start, valid_end)
            ).distinct('date').order_by('date').values('date')),
        )

        # When
        response = self.client.get(reverse('forecast:retrieve-forecasts'), data={
            'end': valid_end.strftime(DATE_FORMAT),
        })
        response_content = loads(response.content)

        # Then
        self.assertListEqual(response_content, expected_forecasts)

    def test_get_forecasts_should_return_method_not_allowed_when_requesting_method_is_post(self):
        # POST로 요청할 경우에 405로 응답해야 한다.
        # Given
        valid_querystring = {
            'start': date(self.this_year, self.this_month, 10).strftime(DATE_FORMAT),
            'end': date(self.this_year, self.this_month, 11).strftime(DATE_FORMAT),
        }

        # When
        response = self.client.post(reverse('forecast:retrieve-forecasts'), data=valid_querystring)

        # Then
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_get_forecasts__should_return_method_not_allowed_when_requesting_method_is_put(self):
        # PUT으로 요청할 경우에 405로 응답해야 한다.
        # Given
        valid_querystring = {
            'start': date(self.this_year, self.this_month, 10).strftime(DATE_FORMAT),
            'end': date(self.this_year, self.this_month, 11).strftime(DATE_FORMAT),
        }

        # When
        response = self.client.put(reverse('forecast:retrieve-forecasts'), data=valid_querystring)

        # Then
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_get_forecasts_should_return_method_not_allowed_when_requesting_method_is_delete(self):
        # DELETE으로 요청할 경우에 405로 응답해야 한다.
        # Given
        valid_querystring = {
            'start': date(self.this_year, self.this_month, 10).strftime(DATE_FORMAT),
            'end': date(self.this_year, self.this_month, 11).strftime(DATE_FORMAT),
        }

        # When
        response = self.client.delete(reverse('forecast:retrieve-forecasts'), data=valid_querystring)

        # Then
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_get_forecasts_should_return_method_not_allowed_when_requesting_method_is_patch(self):
        # PATCH으로 요청할 경우에 405로 응답해야 한다.
        # Given
        valid_querystring = {
            'start': date(self.this_year, self.this_month, 10).strftime(DATE_FORMAT),
            'end': date(self.this_year, self.this_month, 11).strftime(DATE_FORMAT),
        }

        # When
        response = self.client.patch(reverse('forecast:retrieve-forecasts'), data=valid_querystring)

        # Then
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
