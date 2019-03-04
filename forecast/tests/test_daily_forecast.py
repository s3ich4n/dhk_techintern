from unittest.mock import patch
from http import HTTPStatus

from django.test import TestCase
from django.utils import timezone

from configuration.settings.base import WEATHER_PLANET_SERVER_NAME
from forecast.exceptions import ForecastServerResponseException
from forecast.models import Region, Forecast
from forecast.modules.daily_info import get_daily_weather_by_region, update_or_create_daily_forecast
from forecast.tests.common.classes import WeatherEnum


class TestRequestingWeatherPlanet(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestRequestingWeatherPlanet, cls).setUpClass()
        cls.gg_region = Region.objects.create(
            name='경기',
            longitude='127.0977600000',
            latitude='7.1177600000',
            observing_station=300,
        )
        cls.temp_max = 24.0
        cls.temp_min = 12.0
        cls.weather = WeatherEnum.SUN.value
        cls.today_date = timezone.now().strftime('%Y-%m-%d')

    def setUp(self):
        self.new_forecast = {
            'date': self.today_date,
            'temperature': 23.5,
            'weather': self.weather,
            'region': self.gg_region,
        }
        self.already_existing_forecast = Forecast(
            date=self.today_date,
            temperature=17.9,
            weather=WeatherEnum.SUN_DUST.value,
            region=self.gg_region,
        )
        self.response_json = {
            'result': {
                'code': 9200,
                'requestUrl': '/weather/summary?version=2&lat=37.1234&lon=127.1234',
                'message': '성공'
            },
            'common': {
                'alertYn': 'Y',
                'stormYn': 'N'
            },
            'weather': {
                'summary': [
                    {
                        'grid': {
                            'longitude': '127.0977600000',
                            'latitude': '37.1177600000',
                            'city': '경기',
                            'county': '오산시',
                            'village': '청호동'
                        },
                        'timeRelease': '2017-06-02 17:00:00',
                        'yesterday': {
                            'precipitation': {
                                'rain': '0.10',
                                'snow': '0.00'
                            },
                            'sky': {
                                'code': 'SKY_Y05',
                                'name': '비'
                            },
                            'temperature': {
                                'tmax': '25.80',
                                'tmin': '16.70'
                            }
                        },
                        'today': {
                            'sky': {
                                'code': 'SKY_D03',
                                'name': '맑음'
                            },
                            'temperature': {
                                'tmax': '24.00',
                                'tmin': '12.00'
                            }
                        },
                        'tomorrow': {
                            'sky': {
                                'code': 'SKY_M03',
                                'name': '구름많음'
                            },
                            'temperature': {
                                'tmax': '25.00',
                                'tmin': '13.00'
                            }
                        },
                        'dayAfterTomorrow': {
                            'sky': {
                                'code': 'SKY_M01',
                                'name': '맑음'
                            },
                            'temperature': {
                                'tmax': '27.00',
                                'tmin': '12.00'
                            }
                        }
                    }
                ]
            }

        }

    @patch('forecast.modules.daily_info._request_weather_planet_server')
    def test_get_daily_weather_by_region_should_return_forecast_based_on_response_json_content(self, mock_request):
        # Given
        expected_region = self.gg_region
        expected_region_name = self.response_json['weather']['summary'][0]['grid']['city']
        expected_today_date = self.today_date
        expected_today_weather = self.response_json['weather']['summary'][0]['today']['sky']['name']
        expected_today_temp = (float(self.temp_max) + float(self.temp_min)) / 2

        mock_request.return_value = self.response_json

        # When
        forecast = get_daily_weather_by_region(self.gg_region)

        # Then
        self.assertEqual(forecast['date'], expected_today_date)
        self.assertEqual(forecast['weather'], expected_today_weather)
        self.assertEqual(forecast['temperature'], expected_today_temp)
        self.assertEqual(forecast['region'], expected_region)
        self.assertEqual(forecast['region'].name, expected_region_name)

    @patch('forecast.modules.daily_info._request_weather_planet_server')
    def test_get_daily_weather_by_region_should_raise_server_response_exception_when_responsing_401(self, mock_request):
        # Given
        mock_request.side_effect = ForecastServerResponseException(
            status_code=HTTPStatus.UNAUTHORIZED,
            server_name=WEATHER_PLANET_SERVER_NAME,
        )

        # When
        with self.assertRaises(ForecastServerResponseException) as cm:
            get_daily_weather_by_region(self.gg_region)

        # Then
        self.assertIsInstance(cm.exception, ForecastServerResponseException)
        self.assertEqual(cm.exception.status_code, HTTPStatus.UNAUTHORIZED)

    @patch('forecast.modules.daily_info._request_weather_planet_server')
    def test_get_daily_weather_by_region_should_raise_key_err_when_responsing_invalid_format(self, mock_request):
        # Given
        self.response_json['weather']['summary'] = {'message': 'some weird format.'}
        mock_request.return_value = self.response_json

        # When
        with self.assertRaises(KeyError) as cm:
            get_daily_weather_by_region(self.gg_region)

        # Then
        self.assertIsInstance(cm.exception, KeyError)

    @patch('forecast.modules.daily_info._request_weather_planet_server')
    def test_get_daily_weather_by_region_should_raise_type_err_when_responsing_invalid_format(self, mock_request):
        # Given
        self.response_json['weather']['summary'] = 12345
        mock_request.return_value = self.response_json

        # When
        with self.assertRaises(TypeError) as cm:
            get_daily_weather_by_region(self.gg_region)

        # Then
        self.assertIsInstance(cm.exception, TypeError)

    @patch('forecast.modules.daily_info._request_weather_planet_server')
    def test_get_daily_weather_by_region_should_raise_attr_err_when_responsing_invalid_format(self, mock_request):
        # Given
        self.response_json['weather']['summary'][0]['today'] = {'message': 'some weird format.'}
        mock_request.return_value = self.response_json

        # When
        with self.assertRaises(AttributeError) as cm:
            get_daily_weather_by_region(self.gg_region)

        # Then
        self.assertIsInstance(cm.exception, AttributeError)

    @patch('forecast.modules.daily_info._request_weather_planet_server')
    def test_get_daily_weather_by_region_should_raise_value_err_when_responsing_temp_data_not_castable_to_float(self,
                                                                                                                mock_request):
        # Given
        self.response_json['weather']['summary'][0]['today']['temperature']['tmax'] = 'not castable to float.'
        self.response_json['weather']['summary'][0]['today']['temperature']['tmin'] = 'not castable to float, too.'
        mock_request.return_value = self.response_json

        # When
        with self.assertRaises(ValueError) as cm:
            get_daily_weather_by_region(self.gg_region)

        # Then
        self.assertIsInstance(cm.exception, ValueError)

    def test_update_or_create_daily_forecast_should_save_forecasts_when_there_are_no_today_forecasts(self):
        # forecast 테이블에 오늘날짜를 date필드로 갖는 row가 아예 없으면 새로운 row를 삽입해야 한다.
        # Given
        Forecast.objects.filter(date=self.today_date).delete()
        expected_forecast = self.new_forecast

        # When
        update_or_create_daily_forecast(self.new_forecast)
        saved_forecast = Forecast.objects.get(date=self.today_date, region=self.gg_region)

        # Then
        self.assertEqual(saved_forecast.weather, expected_forecast['weather'])
        self.assertEqual(saved_forecast.temperature, expected_forecast['temperature'])
        self.assertEqual(saved_forecast.date.strftime('%Y-%m-%d'), expected_forecast['date'])
        self.assertEqual(saved_forecast.region, expected_forecast['region'])

    def test_update_or_create_daily_forecast_should_update_temperature_when_there_is_forecast_with_null_temperature(
            self):
        # forecast 테이블에 오늘날짜를 date필드로 갖는 row가 있으면 해당 row를 갱신해야 한다.
        # Given
        expected_forecast = self.new_forecast
        Forecast.objects.filter(date=self.today_date).delete()
        forecast = self.already_existing_forecast
        forecast.save()

        # When
        update_or_create_daily_forecast(self.new_forecast)
        saved_forecast = Forecast.objects.get(date=self.today_date, region=self.gg_region)

        # Then
        self.assertEqual(saved_forecast.weather, expected_forecast['weather'])
        self.assertEqual(saved_forecast.temperature, expected_forecast['temperature'])
        self.assertEqual(saved_forecast.date.strftime('%Y-%m-%d'), expected_forecast['date'])
        self.assertEqual(saved_forecast.region, expected_forecast['region'])

    def test_update_or_create_daily_forecast_should_cleanse_cloud_as_cloudy_when_saving_forecast(self):
        # forecast 테이블에 날씨정보를 저장할 때 '구름'이 들어간 날씨텍스트는 무조건 '흐림'으로 처리하고 저장해야 한다.
        # Given
        Forecast.objects.filter(date=self.today_date).delete()
        new_forecast = {
            'date': self.today_date,
            'temperature': 23.5,
            'weather': '구름많음',
            'region': self.gg_region,
        }
        expected_weather = '흐림'

        # When
        update_or_create_daily_forecast(new_forecast)
        saved_forecast = Forecast.objects.get(date=self.today_date, region=self.gg_region)

        # Then
        self.assertEqual(saved_forecast.weather, expected_weather)

    def test_update_or_create_daily_forecast_should_cleanse_bolt_as_thunder_when_saving_forecast(self):
        # forecast 테이블에 날씨정보를 저장할 때 '번개'가 들어간 날씨텍스트는 무조건 '천둥'으로 처리하고 저장해야 한다.
        # Given
        Forecast.objects.filter(date=self.today_date).delete()
        new_forecast = {
            'date': self.today_date,
            'temperature': 23.5,
            'weather': '번개내리침',
            'region': self.gg_region,
        }
        expected_weather = '천둥'

        # When
        update_or_create_daily_forecast(new_forecast)
        saved_forecast = Forecast.objects.get(date=self.today_date, region=self.gg_region)

        # Then
        self.assertEqual(saved_forecast.weather, expected_weather)

    def test_update_or_create_daily_forecast_should_cleanse_shower_as_rain_when_saving_forecast(self):
        # forecast 테이블에 날씨정보를 저장할 때 '소나기'가 들어간 날씨텍스트는 무조건 '비'로 처리하고 저장해야 한다.
        # Given
        Forecast.objects.filter(date=self.today_date).delete()
        new_forecast = {
            'date': self.today_date,
            'temperature': 23.5,
            'weather': '소나기',
            'region': self.gg_region,
        }
        expected_weather = '비'

        # When
        update_or_create_daily_forecast(new_forecast)
        saved_forecast = Forecast.objects.get(date=self.today_date, region=self.gg_region)

        # Then
        self.assertEqual(saved_forecast.weather, expected_weather)

    def test_update_or_create_daily_forecast_should_cleanse_unknown_as_unknown_when_saving_forecast(self):
        # forecast 테이블에 날씨정보를 저장할 때 정제된 날씨단어가 맑음, 비, 눈, 우박, 황사, 안개, 천둥, 흐림 이외의 단어만을 가지고 있으면
        # '알수없음' 으로 저장되어야 한다.

        # Given
        Forecast.objects.filter(date=self.today_date).delete()
        new_forecast = {
            'date': self.today_date,
            'temperature': 23.5,
            'weather': '햇무리',
            'region': self.gg_region,
        }
        expected_weather = '알수없음'

        # When
        update_or_create_daily_forecast(new_forecast)
        saved_forecast = Forecast.objects.get(date=self.today_date, region=self.gg_region)

        # Then
        self.assertEqual(saved_forecast.weather, expected_weather)

    def test_update_or_create_daily_forecast_should_remove_only_unknown_word_when_saving_forecast(self):
        # forecast 테이블에 날씨정보를 저장할 때 오로지 맑음, 비, 눈, 우박, 황사, 안개, 천둥, 흐림 이외의 단어만을 지워야 한다.

        # Given
        Forecast.objects.filter(date=self.today_date).delete()
        new_forecast = {
            'date': self.today_date,
            'temperature': 23.5,
            'weather': '햇무리, 안개',
            'region': self.gg_region,
        }
        expected_weather = '안개'

        # When
        update_or_create_daily_forecast(new_forecast)
        saved_forecast = Forecast.objects.get(date=self.today_date, region=self.gg_region)

        # Then
        self.assertEqual(saved_forecast.weather, expected_weather)

    def test_update_or_create_daily_forecast_should_cleanse_duplicate_as_uniq_when_saving_forecast(self):
        # forecast 테이블에 날씨정보를 저장할 때 중복되는 개념들의 단어들은 없애고 저장해야 한다.
        # Given
        Forecast.objects.filter(date=self.today_date).delete()
        new_forecast = {
            'date': self.today_date,
            'temperature': 23.5,
            'weather': '구름많음, 흐림, 소나기, 비, 천둥, 번개, ',
            'region': self.gg_region,
        }
        expected_weather = ['비', '천둥', '흐림']

        # When
        update_or_create_daily_forecast(new_forecast)
        saved_forecast = Forecast.objects.get(date=self.today_date, region=self.gg_region)
        saved_forecast_weathers = sorted(saved_forecast.weather.split('/'))

        # Then
        self.assertListEqual(saved_forecast_weathers, expected_weather)
