import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.conf import settings


def weekend_distinction(today):
    _WEEKEND = 5

    if today.weekday() >= _WEEKEND:
        return False
    else:
        return True


def parse_holiday_data(today):
    target_year = today.strftime('%Y')
    target_month = today.strftime('%m')
    endpoint_url = settings.ENDPOINT_URL
    api_key = settings.OPENAPI_KEY

    endpoint = f'{endpoint_url}?solYear={target_year}&solMonth={target_month}&ServiceKey={api_key}'

    xmldata = requests.get(endpoint)

    soup = BeautifulSoup(xmldata.text, 'xml')
    total_count = soup.find('totalCount')

    if total_count.string != '0':
        holidays = [datetime.strptime(date_val.string, '%Y%m%d').strftime('%Y-%m-%d')
                    for date_val in soup.find('items').find_all('locdate')]

        for date in holidays:
            if today.strftime('%Y-%m-%d') == date:
                return False

    return True


def main():
    """
    :return:
    주말이면 False
    주중인데 휴일이면 False
    주중이고 휴일이 아니면 True
    """
    today = datetime.now()

    if weekend_distinction(today):
        return parse_holiday_data(today)
    else:
        return


if __name__ == "__main__":
    if not main():
        sys.exit("holiday")
    else:
        sys.exit("weekday")
