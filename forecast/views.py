from http import HTTPStatus
from datetime import datetime, date
from calendar import monthrange

from dateutil.relativedelta import relativedelta
from django.db.models import F
from django.http import JsonResponse, HttpResponse

from forecast.common.constants import DATE_FORMAT
from forecast.exceptions import InvalidParameterException
from forecast.models import Forecast


def cleanse_start_end_params(start, end):
    if not start and not end:
        today = date.today()
        cleansed_start = datetime(today.year, today.month, 1)
        # monthrange(year, month)의 리턴값: tuple(month의 마지막 날의 요일, month의 마지막 날의 날짜)
        # 마지막 날의 날짜만 필요하므로 인덱스 1 참조.
        cleansed_end = datetime(today.year, today.month, monthrange(today.year, today.month)[1])
    if start and end:
        try:
            parsed_start = datetime.strptime(start, DATE_FORMAT)
            parsed_end = datetime.strptime(end, DATE_FORMAT)
        except ValueError:
            raise InvalidParameterException()
        if parsed_start <= parsed_end:
            cleansed_start = parsed_start
            cleansed_end = parsed_end
        else:
            raise InvalidParameterException('start는 end보다 이른 날짜여야 합니다.')
    if start and not end:
        try:
            parsed_start = datetime.strptime(start, DATE_FORMAT)
        except ValueError:
            raise InvalidParameterException('start의 값이 유효하지 않습니다.')
        cleansed_start = parsed_start
        cleansed_end = cleansed_start + relativedelta(months=1)
    if not start and end:
        try:
            parsed_end = datetime.strptime(end, DATE_FORMAT)
        except ValueError:
            raise InvalidParameterException('end의 값이 유효하지 않습니다.')
        cleansed_end = parsed_end
        cleansed_start = cleansed_end - relativedelta(months=1)

    return cleansed_start.strftime(DATE_FORMAT), cleansed_end.strftime(DATE_FORMAT)


def retrieve_filtered_forecasts_from_db(start, end):
    return Forecast.objects.select_related('region').filter(date__range=(start, end)).values(
        'weather',
        'temperature',
        'date',
        region_name=F('region__name'),
    )


def retrieve_filtered_dates_from_db(start, end):
    return Forecast.objects.filter(date__range=(start, end)).distinct('date').order_by('date').values('date')


def reshape_forecast_list_to_response_body(forecast_list_from_db, dates_from_db):
    reshaped_content = []
    forecast_dict = {}
    if dates_from_db:
        for date_ in dates_from_db:
            date_string = date_['date'].strftime(DATE_FORMAT)
            reshaped_content.append({
                'date': date_string,
            })
            forecast_dict[date_string] = []

    for f in forecast_list_from_db:
        formatted_date = f['date'].strftime(DATE_FORMAT)
        f['date'] = formatted_date
        f['weather'] = f['weather'].split('/')
        forecast_dict.get(formatted_date).append(f)

    for element in reshaped_content:
        element['forecasts'] = forecast_dict.get(element['date'])

    return reshaped_content


def get_forecasts(request):
    if request.method != 'GET':
        return HttpResponse(
            status=HTTPStatus.METHOD_NOT_ALLOWED,
        )
    try:
        cleansed_start, cleansed_end = cleanse_start_end_params(
            start=request.GET.get('start'),
            end=request.GET.get('end'),
        )
    except InvalidParameterException as err:
        return JsonResponse(
            data={
                'message': err.message,
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    forecast_queryset = retrieve_filtered_forecasts_from_db(
        start=cleansed_start,
        end=cleansed_end,
    )
    date_queryset = retrieve_filtered_dates_from_db(
        start=cleansed_start,
        end=cleansed_end,
    )
    forecasts = list(forecast_queryset)
    dates = list(date_queryset)

    content = reshape_forecast_list_to_response_body(
        forecast_list_from_db=forecasts,
        dates_from_db=dates,
    )

    response = JsonResponse(content, safe=False)
    if not forecasts:
        response.status_code = HTTPStatus.NO_CONTENT
    return response
