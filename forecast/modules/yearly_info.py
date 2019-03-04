from datetime import date
from calendar import monthrange

from bs4 import BeautifulSoup
from requests import get

from configuration.settings.base import (
    GISANG_TEMP_PAGE_NAME,
    GISANG_WEATHER_PAGE_NAME,
    GISANG_WEATHER_OBS,
    GISANG_TEMPERATURE_OBS,
    GISANG_URL,
)

from forecast.exceptions import handle_invalid_server_response
from forecast.modules.common import _cleanse_weather_text

DAY_MAX = 31
MONTH_MAX = 12


def _crawl_page(page_name, GISANG_URL, params):
    response = get(GISANG_URL, params=params)
    handle_invalid_server_response(
        response=response,
        server_name=page_name,
    )
    return response


def _get_table_body(page_name, response):
    soup = BeautifulSoup(response.text, "lxml-xml")
    try:
        table = soup.find("table", {"summary": "일평균기온을 안내한 표입니다."})
        tbody = table.find("tbody")
    except AttributeError as attr_err:
        raise AttributeError(f"{_get_table_body.__name__}(): {page_name} occurs '{attr_err}'.")
    return tbody


def _get_table_data_by_day(page_name, tbody, day_idx):
    try:
        temp_row_per_day = tbody.find_all("tr")[day_idx]
    except IndexError as idx_err:
        raise IndexError(f"{_get_table_data_by_day.__name__}(): {page_name} occurs '{idx_err}'.")
    try:
        table_data = temp_row_per_day.find("td", {"scope": "row"}).find_next_siblings("td")
    except AttributeError as attr_err:
        raise AttributeError(f"{_get_table_data_by_day.__name__}(): {page_name} occurs '{attr_err}'.")
    return table_data


def create_date(year, month, day):
    try:
        created_date = date(year, month, day).strftime("%Y-%m-%d")
    except ValueError:
        return None
    return created_date


def get_all_dates_by_year(year):
    # monthrange() 리턴 값: tuple. (month의 1일의 요일, month의 일수).
    # month의 일수만 필요하므로 인덱스 1만 참조.
    all_dates = []
    for month in range(1, MONTH_MAX + 1):
        days = monthrange(year, month)[1]
        for day in range(1, days + 1):
            all_dates.append(create_date(year, month, day))
    return all_dates


def _parse_temperatures_from_response(region, year):
    temp_params = {
        "stn": region.observing_station,
        "yy": year,
        "obs": GISANG_TEMPERATURE_OBS,
    }
    response = _crawl_page(page_name=GISANG_TEMP_PAGE_NAME, GISANG_URL=GISANG_URL, params=temp_params)
    temp_tbody = _get_table_body(page_name=GISANG_TEMP_PAGE_NAME, response=response)
    all_dates_in_year = get_all_dates_by_year(year)
    parsed_temperatures = {}

    for day_idx in range(0, DAY_MAX):
        day = day_idx + 1
        temp_elements = _get_table_data_by_day(page_name=GISANG_TEMP_PAGE_NAME, tbody=temp_tbody, day_idx=day_idx)
        for month_idx in range(0, MONTH_MAX):
            month = month_idx + 1
            try:
                temperature = temp_elements[month_idx]
            except IndexError as idx_err:
                err_msg = f"{_parse_temperatures_from_response.__name__}(): {GISANG_TEMP_PAGE_NAME} occurs '{idx_err}'."
                raise IndexError(err_msg)
            date_ = create_date(year, month, day)
            if date_ in all_dates_in_year:
                parsed_temperatures.update({
                    date_: temperature.text,
                })
    return parsed_temperatures


def _parse_weathers_from_response(region, year):
    weather_params = {
        "stn": region.observing_station,
        "yy": year,
        "obs": GISANG_WEATHER_OBS,
    }
    response = _crawl_page(page_name=GISANG_WEATHER_PAGE_NAME, GISANG_URL=GISANG_URL, params=weather_params)
    weather_tbody = _get_table_body(page_name=GISANG_WEATHER_PAGE_NAME, response=response)

    all_dates_in_year = get_all_dates_by_year(year)
    parsed_weathers = {}
    for day_idx in range(0, DAY_MAX):
        day = day_idx + 1
        weather_elements = _get_table_data_by_day(page_name=GISANG_TEMP_PAGE_NAME, tbody=weather_tbody, day_idx=day_idx)
        for month_idx in range(0, MONTH_MAX):
            month = month_idx + 1
            try:
                weather = weather_elements[month_idx]
            except IndexError as idx_err:
                err_msg = f"{_parse_weathers_from_response.__name__}(): {GISANG_WEATHER_PAGE_NAME} occurs '{idx_err}'."
                raise IndexError(err_msg)
            date_ = create_date(year, month, day)
            if date_ in all_dates_in_year:
                parsed_weathers.update({
                    date_: weather.text,
                })
    return parsed_weathers


def _cleanse_temperature_text(temp_text):
    if temp_text == "":
        return None
    return float(temp_text)


def get_yearly_forecasts_by_region(region, year):
    parsed_temperatures = _parse_temperatures_from_response(region, year)
    parsed_weathers = _parse_weathers_from_response(region, year)
    return [
        {
            'temperature': _cleanse_temperature_text(parsed_temperatures.get(date_)),
            'weather': _cleanse_weather_text(parsed_weathers.get(date_)),
            'region': region,
            'date': date_,
        }
        for date_ in get_all_dates_by_year(year)
    ]
