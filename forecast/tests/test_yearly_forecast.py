from http import HTTPStatus
from unittest.mock import patch
from random import choice

from django.test import TestCase

from configuration.settings.base import GISANG_WEATHER_PAGE_NAME, GISANG_TEMP_PAGE_NAME
from forecast.exceptions import ForecastServerResponseException
from forecast.models import Region, Forecast
from forecast.modules.yearly_info import get_yearly_forecasts_by_region, get_all_dates_by_year
from forecast.tests.common.classes import WeatherEnum, RegionEnum


def create_yearly_dict_by_random_choice(iter_list, choice_list):
    dict_ = {}
    [dict_.update({key: choice(choice_list)}) for key in iter_list]
    return dict_


class TestRequestingWeatherPlanet(TestCase):
    fixtures = [
        'region.json',
    ]

    @classmethod
    def setUpClass(cls):
        super(TestRequestingWeatherPlanet, cls).setUpClass()
        cls.seoul_region = Region.objects.get(name=RegionEnum.SEOUL.value)
        cls.year = 2018
        cls.all_dates = get_all_dates_by_year(cls.year)
        cls.temperatures = ['5.8', '16.2', '34.7', '-2.1']
        cls.partial_temperatures = ['5.8', '16.2', '', '34.7', '']
        cls.partial_weathers = [
            WeatherEnum.RAINDROPS.value,
            WeatherEnum.SUN_DUST.value,
            '',
            '',
            WeatherEnum.THUNDERSTORM.value,
        ]

        cls.not_empty_parsed_temperatures = create_yearly_dict_by_random_choice(
            iter_list=cls.all_dates,
            choice_list=cls.temperatures,
        )
        cls.not_empty_parsed_weathers = create_yearly_dict_by_random_choice(
            iter_list=cls.all_dates,
            choice_list=list(WeatherEnum),
        )
        for key, w_enum in cls.not_empty_parsed_weathers.items():
            cls.not_empty_parsed_weathers[key] = w_enum.value

        cls.partially_empty_parsed_temperatures = create_yearly_dict_by_random_choice(
            iter_list=cls.all_dates,
            choice_list=cls.partial_temperatures,
        )
        cls.partially_empty_parsed_weathers = create_yearly_dict_by_random_choice(
            iter_list=cls.all_dates,
            choice_list=cls.partial_weathers,
        )
        cls.totally_empty_parsed_temperatures = create_yearly_dict_by_random_choice(
            iter_list=cls.all_dates,
            choice_list=['']
        )
        cls.totally_empty_parsed_weathers = create_yearly_dict_by_random_choice(
            iter_list=cls.all_dates,
            choice_list=[''],
        )

    @staticmethod
    def get_random_invalid_response():
        expected_server_status = HTTPStatus.OK
        while expected_server_status == HTTPStatus.OK:
            expected_server_status = choice(list(HTTPStatus))
        return expected_server_status

    @patch('forecast.modules.yearly_info._parse_temperatures_from_response')
    @patch('forecast.modules.yearly_info._parse_weathers_from_response')
    def test_get_yearly_forecasts_by_region_should_return_forecast_list_when_parsing_not_empty_data(self,
                                                                                                    mock_weather_req,
                                                                                                    mock_temp_req):
        # 파싱해온 2018년 1/1 ~ 12/31 평균기온/날씨에 모두 빈 문자열이 없을 경우,
        # get_yearly_forecasts_by_region은 각 날짜에 해당하는 평균기온/날씨 값을 갖는 forecast 객체리스트를 리턴해야 한다.

        # Given
        mock_temp_req.return_value = self.not_empty_parsed_temperatures
        mock_weather_req.return_value = self.not_empty_parsed_weathers

        expected_region = self.seoul_region
        expected_yearly_forecasts = [Forecast(
            region=expected_region,
            weather=mock_weather_req.return_value.get(date_),
            temperature=float(mock_temp_req.return_value.get(date_)),
            date=date_
        )
            for date_ in self.all_dates
        ]

        # When
        returned_yearly_forecasts = get_yearly_forecasts_by_region(region=expected_region, year=self.year)
        returned_yearly_forecasts.sort(key=lambda f: f['date'])

        # Then
        for returned_element, expected_element in zip(returned_yearly_forecasts, expected_yearly_forecasts):
            self.assertEqual(returned_element['date'], expected_element.date)
            self.assertEqual(returned_element['temperature'], expected_element.temperature)
            self.assertEqual(returned_element['weather'], expected_element.weather)
            self.assertEqual(returned_element['region'], expected_element.region)

    @patch('forecast.modules.yearly_info._parse_temperatures_from_response')
    @patch('forecast.modules.yearly_info._parse_weathers_from_response')
    def test_get_yearly_forecasts_by_region_should_return_forecast_list_when_parsing_empty_temperatures_partially(self,
                                                                                                                  mock_weather_req,
                                                                                                                  mock_temp_req):
        # 파싱해온 2018년 1/1 ~ 12/31의 평균기온 중에 일부 빈 문자열이 있을 경우,
        # get_yearly_forecasts_by_region은 해당 평균기온 필드가 None인 일부 forecast을 포함한 리스트를 리턴해야 한다.

        # Given
        mock_temp_req.return_value = self.partially_empty_parsed_temperatures
        mock_weather_req.return_value = self.not_empty_parsed_weathers

        expected_region = self.seoul_region
        expected_yearly_forecasts = [Forecast(
            region=expected_region,
            weather=mock_weather_req.return_value.get(date_),
            temperature=None
            if mock_temp_req.return_value.get(date_) == ''
            else float(mock_temp_req.return_value.get(date_)),
            date=date_
        )
            for date_ in self.all_dates
        ]

        # When
        returned_yearly_forecasts = get_yearly_forecasts_by_region(region=expected_region, year=self.year)
        returned_yearly_forecasts.sort(key=lambda f: f['date'])

        # Then
        for returned_element, expected_element in zip(returned_yearly_forecasts, expected_yearly_forecasts):
            self.assertEqual(returned_element['date'], expected_element.date)
            self.assertEqual(returned_element['temperature'], expected_element.temperature)
            self.assertEqual(returned_element['weather'], expected_element.weather)
            self.assertEqual(returned_element['region'], expected_element.region)

    @patch('forecast.modules.yearly_info._parse_temperatures_from_response')
    @patch('forecast.modules.yearly_info._parse_weathers_from_response')
    def test_get_yearly_forecasts_by_region_should_return_forecast_list_when_parsing_empty_weathers_partially(self,
                                                                                                              mock_weather_req,
                                                                                                              mock_temp_req):
        # 파싱해온 2018년 1/1 ~ 12/31의 날씨 중에 일부 빈 문자열이 있을 경우,
        # get_yearly_forecasts_by_region은 해당 날씨 필드가 '맑음'인 일부 forecast을 포함한 리스트를 리턴해야 한다.

        # Given
        mock_temp_req.return_value = self.not_empty_parsed_temperatures
        mock_weather_req.return_value = self.partially_empty_parsed_weathers

        expected_region = self.seoul_region
        expected_yearly_forecasts = [Forecast(
            region=expected_region,
            weather=WeatherEnum.SUN.value
            if mock_weather_req.return_value.get(date_) == ''
            else mock_weather_req.return_value.get(date_),
            temperature=float(mock_temp_req.return_value.get(date_)),
            date=date_
        )
            for date_ in self.all_dates
        ]

        # When
        returned_yearly_forecasts = get_yearly_forecasts_by_region(region=expected_region, year=self.year)
        returned_yearly_forecasts.sort(key=lambda f: f['date'])

        # Then
        for returned_element, expected_element in zip(returned_yearly_forecasts, expected_yearly_forecasts):
            self.assertEqual(returned_element['date'], expected_element.date)
            self.assertEqual(returned_element['temperature'], expected_element.temperature)
            self.assertEqual(returned_element['weather'], expected_element.weather)
            self.assertEqual(returned_element['region'], expected_element.region)

    @patch('forecast.modules.yearly_info._parse_temperatures_from_response')
    @patch('forecast.modules.yearly_info._parse_weathers_from_response')
    def test_get_yearly_forecasts_by_region_should_return_forecast_list_when_parsing_empty_temperatures_totally(self,
                                                                                                                mock_weather_req,
                                                                                                                mock_temp_req):
        # 파싱해온 2018년 1/1 ~ 12/31의 평균기온이 모두 빈 문자열일 경우,
        # get_yearly_forecasts_by_region은 temperature필드가 None인 forecast 리스트를 리턴해야 한다.

        # Given
        mock_temp_req.return_value = self.totally_empty_parsed_temperatures
        mock_weather_req.return_value = self.not_empty_parsed_weathers

        expected_region = self.seoul_region
        expected_yearly_forecasts = [Forecast(
            region=expected_region,
            weather=mock_weather_req.return_value.get(date_),
            temperature=None
            if mock_temp_req.return_value.get(date_) == ''
            else float(mock_temp_req.return_value.get(date_)),
            date=date_
        )
            for date_ in self.all_dates
        ]

        # When
        returned_yearly_forecasts = get_yearly_forecasts_by_region(region=expected_region, year=self.year)
        returned_yearly_forecasts.sort(key=lambda f: f['date'])

        # Then
        for returned_element, expected_element in zip(returned_yearly_forecasts, expected_yearly_forecasts):
            self.assertEqual(returned_element['date'], expected_element.date)
            self.assertEqual(returned_element['temperature'], expected_element.temperature)
            self.assertEqual(returned_element['weather'], expected_element.weather)
            self.assertEqual(returned_element['region'], expected_element.region)

    @patch('forecast.modules.yearly_info._parse_temperatures_from_response')
    @patch('forecast.modules.yearly_info._parse_weathers_from_response')
    def test_get_yearly_forecasts_by_region_should_return_forecast_list_when_parsing_empty_weathers_totally(self,
                                                                                                            mock_weather_req,
                                                                                                            mock_temp_req):
        # 파싱해온 2018년 1/1 ~ 12/31의 날씨가 모두 빈 문자열일 경우,
        # get_yearly_forecasts_by_region은 weather 필드가 '맑음'인 forecast 리스트를 리턴해야 한다.

        # Given
        mock_temp_req.return_value = self.not_empty_parsed_temperatures
        mock_weather_req.return_value = self.totally_empty_parsed_temperatures

        expected_region = self.seoul_region
        expected_yearly_forecasts = [Forecast(
            region=expected_region,
            weather='맑음'
            if mock_weather_req.return_value.get(date_) == ''
            else mock_weather_req.return_value.get(date_),
            temperature=float(mock_temp_req.return_value.get(date_)),
            date=date_
        )
            for date_ in self.all_dates
        ]

        # When
        returned_yearly_forecasts = get_yearly_forecasts_by_region(region=expected_region, year=self.year)
        returned_yearly_forecasts.sort(key=lambda f: f['date'])

        # Then
        for returned_element, expected_element in zip(returned_yearly_forecasts, expected_yearly_forecasts):
            self.assertEqual(returned_element['date'], expected_element.date)
            self.assertEqual(returned_element['temperature'], expected_element.temperature)
            self.assertEqual(returned_element['weather'], expected_element.weather)
            self.assertEqual(returned_element['region'], expected_element.region)

    @patch('forecast.modules.yearly_info._parse_temperatures_from_response')
    def test_get_yearly_forecasts_by_region_should_raise_server_exception_when_temperature_response_is_not_ok(self,
                                                                                                              mock_temp_req):
        # 평균기온을 제공하는 기상청 페이지의 응답 상태가 30x, 40x, 50x일 경우
        # get_yearly_forecasts_by_region은 ForecastServerResponseException 예외를 던져야 한다.

        # Given
        expected_server_status = self.get_random_invalid_response()
        mock_temp_req.side_effect = ForecastServerResponseException(
            status_code=expected_server_status,
            server_name=GISANG_TEMP_PAGE_NAME,
        )

        # When
        with self.assertRaises(ForecastServerResponseException) as cm:
            get_yearly_forecasts_by_region(region=self.seoul_region, year=self.year)

        # Then
        self.assertIsInstance(cm.exception, ForecastServerResponseException)
        self.assertEqual(cm.exception.status_code, expected_server_status)
        self.assertEqual(cm.exception.server_name, GISANG_TEMP_PAGE_NAME)

    @patch('forecast.modules.yearly_info._parse_weathers_from_response')
    def test_get_yearly_forecasts_by_region_should_raise_server_exception_when_weather_response_is_not_ok(self,
                                                                                                          mock_weather_req):
        # 날씨를 제공하는 기상청 페이지의 응답 상태가 30x, 40x, 50x일 경우
        # get_yearly_forecasts_by_region은 ForecastServerResponseException 예외를 던져야 한다.

        # Given
        expected_server_status = self.get_random_invalid_response()
        mock_weather_req.side_effect = ForecastServerResponseException(
            status_code=expected_server_status,
            server_name=GISANG_WEATHER_PAGE_NAME,
        )

        # When
        with self.assertRaises(ForecastServerResponseException) as cm:
            get_yearly_forecasts_by_region(region=self.seoul_region, year=self.year)

        # Then
        self.assertIsInstance(cm.exception, ForecastServerResponseException)
        self.assertEqual(cm.exception.status_code, expected_server_status)
        self.assertEqual(cm.exception.server_name, GISANG_WEATHER_PAGE_NAME)

    @patch('forecast.modules.yearly_info._parse_temperatures_from_response')
    def test_get_yearly_forecasts_by_region_should_raise_server_exception_when_parsing_temperatures_occurs_index_error(
            self,
            mock_temp_req):
        # 평균기온을 제공하는 기상청 페이지를 긁어와서 파싱하는 도중 index error가 발생할 경우
        # get_yearly_forecasts_by_region은 IndexError 예외를 던져야 한다.

        # Given
        mock_temp_req.side_effect = IndexError()

        # When
        with self.assertRaises(IndexError) as cm:
            get_yearly_forecasts_by_region(region=self.seoul_region, year=self.year)

        # Then
        self.assertIsInstance(cm.exception, IndexError)

    @patch('forecast.modules.yearly_info._parse_weathers_from_response')
    def test_get_yearly_forecasts_by_region_should_raise_server_exception_when_parsing_weathers_occurs_index_error(self,
                                                                                                                   mock_weather_req):
        # 날씨를 제공하는 기상청 페이지를 긁어와서 파싱하는 도중 index error가 발생할 경우
        # get_yearly_forecasts_by_region은 IndexError 예외를 던져야 한다.

        # Given
        mock_weather_req.side_effect = IndexError()

        # When
        with self.assertRaises(IndexError) as cm:
            get_yearly_forecasts_by_region(region=self.seoul_region, year=self.year)

        # Then
        self.assertIsInstance(cm.exception, IndexError)

    @patch('forecast.modules.yearly_info._parse_temperatures_from_response')
    def test_get_yearly_forecasts_by_region_should_raise_server_exception_when_parsing_temperatures_occurs_attribute_error(
            self,
            mock_temp_req):
        # 평균기온을 제공하는 기상청 페이지를 긁어와서 파싱하는 도중 attribute error가 발생할 경우
        # get_yearly_forecasts_by_region은 AttributeError 예외를 던져야 한다.

        # Given
        mock_temp_req.side_effect = AttributeError()

        # When
        with self.assertRaises(AttributeError) as cm:
            get_yearly_forecasts_by_region(region=self.seoul_region, year=self.year)

        # Then
        self.assertIsInstance(cm.exception, AttributeError)

    @patch('forecast.modules.yearly_info._parse_weathers_from_response')
    def test_get_yearly_forecasts_by_region_should_raise_server_exception_when_parsing_weathers_occurs_attribute_error(
            self,
            mock_weather_req):
        # 평균기온을 제공하는 기상청 페이지를 긁어와서 파싱하는 도중 attribute error가 발생할 경우
        # get_yearly_forecasts_by_region은 AttributeError 예외를 던져야 한다.

        # Given
        mock_weather_req.side_effect = AttributeError()

        # When
        with self.assertRaises(AttributeError) as cm:
            get_yearly_forecasts_by_region(region=self.seoul_region, year=self.year)

        # Then
        self.assertIsInstance(cm.exception, AttributeError)
