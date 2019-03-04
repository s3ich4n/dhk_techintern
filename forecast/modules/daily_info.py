from django.utils import timezone
from requests import get

from django.conf import settings

from configuration.settings.base import WEATHER_PLANET_URL, WEATHER_PLANET_SERVER_NAME, WEATHER_PLANET_API_VERSION
from forecast.common.constants import DATE_FORMAT
from forecast.models import Forecast
from forecast.exceptions import handle_invalid_server_response
from forecast.modules.common import _cleanse_weather_text

HEADER_FOR_REQUEST = {
    "appKey": settings.WEATHER_PLANET_API_KEY,
    "Accept": "application/json;charset=utf-8;",
    "Content-Type": "application/json",
}


def _request_weather_planet_server(region):
    parameters = {
        "version": WEATHER_PLANET_API_VERSION,
        "latitude": region.latitude,
        "longitude": region.longitude,
        "stnid": region.observing_station,
    }
    response = get(WEATHER_PLANET_URL, params=parameters, headers=HEADER_FOR_REQUEST)
    handle_invalid_server_response(
        response=response,
        server_name=WEATHER_PLANET_SERVER_NAME,
    )
    return response.json()


def _format_response_json(res_json):
    err_msg = f"{_format_response_json.__name__}(): {WEATHER_PLANET_SERVER_NAME} occurs '%s' "
    try:
        summarized_info = res_json.get("weather").get("summary")
    except AttributeError as attr_err:
        err_msg += "while accessing summarized info."
        raise AttributeError(err_msg % attr_err)

    try:
        # summary는 요소 갯수가 1개인 배열이므로 0보다 큰 인덱스는 없다.
        # (https://weatherplanet.docs.apiary.io/#introduction 의 간편날씨 example 참고.)
        actual_summarized_info = summarized_info[0]
    except TypeError as type_err:
        err_msg += "while accessing first element of summarized info."
        raise TypeError(err_msg % type_err)
    except KeyError as key_err:
        err_msg += "while accessing first element of summarized info."
        raise KeyError(err_msg % key_err)

    try:
        today_info = actual_summarized_info.get("today")
        weather = today_info.get("sky").get("name")
        temp_max = today_info.get("temperature").get("tmax")
        temp_min = today_info.get("temperature").get("tmin")
    except AttributeError as attr_err:
        err_msg += "while accessing temp and weather."
        raise AttributeError(err_msg % attr_err)

    return {
        "tmax": temp_max,
        "tmin": temp_min,
        "weather": weather,
    }


def get_daily_weather_by_region(region):
    response_json = _request_weather_planet_server(region)
    today_info = _format_response_json(response_json)
    try:
        forecast = {
            'date': timezone.now().strftime(DATE_FORMAT),
            'weather': today_info.get('weather'),
            'temperature': (float(today_info.get('tmax')) + float(today_info.get('tmin'))) / 2,
            'region': region,
        }
    except ValueError as val_err:
        err_msg = f"{get_daily_weather_by_region.__name__}(): " \
                  f"{WEATHER_PLANET_SERVER_NAME} occurs '{val_err}' while converting temp to float."
        raise ValueError(err_msg)
    return forecast


def update_or_create_daily_forecast(response_forecast):
    Forecast.objects.update_or_create(
        date=response_forecast.get('date'),
        region=response_forecast.get('region'),
        defaults={
            'weather': _cleanse_weather_text(response_forecast.get('weather')),
            'temperature': response_forecast.get('temperature')
        }
    )
