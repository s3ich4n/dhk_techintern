import datetime
import json
import re
from http import HTTPStatus

import pytz
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils.timezone import make_aware
from django.views import View

from account import mixin
from schedule.forms import EventForm
from schedule.models import Event


def get_data_from_db(data_set):
    kst_tz = pytz.timezone(settings.TIME_ZONE)

    rename_list = [
        {
            'id': values['id'],
            'title': values['title'],
            'start': values['start_at'].astimezone(tz=kst_tz).strftime('%Y-%m-%d %H:%M:%S%z'),
            'end': values['end_at'].astimezone(tz=kst_tz).strftime('%Y-%m-%d %H:%M:%S%z'),
            'description': values['description'],
            'author': values['author'],
            'category': values['category'],
            'is_allday': values['is_allday'],
        } for values in data_set
    ]
    return rename_list


class RetrieveMonthlyEvent(mixin.LoginRequiredMixin,
                           mixin.PermissionRequiredMixin,
                           View):
    """
    POST: 새로운 이벤트를 생성하는 뷰
    GET: 월별 달력내에 해당하는 이벤트를 가지고 오는 뷰
    """
    model = Event
    context_object_name = 'date_info'

    permission_required = {
        'GET': ('schedule.view_event',),
        'POST': ('schedule.add_event',),
    }

    @staticmethod
    def post(request):
        data_need_cleaned = {
            'title': request.POST.get('title'),
            'category': request.POST.get('category'),
            'author': request.POST.get('author'),
            'description': request.POST.get('description'),
            'is_allday': request.POST.get('is_allday'),
            'start_at': request.POST.get('start_at').strip(),
            'end_at': request.POST.get('end_at').strip(),
            'start_at_type': request.POST.get('start_at_type'),
            'end_at_type': request.POST.get('end_at_type'),
        }
        form = EventForm(data_need_cleaned)
        if not form.is_valid():
            msg = {k: v[0] for k, v in form.errors.items()}
            if msg.get('__all__'):
                msg['start_at'] = msg['__all__']
                del msg['__all__']
            return JsonResponse(
                status=400,
                data=msg,
            )
        event_required_keys = ['title', 'category', 'author', 'description', 'start_at', 'end_at', 'is_allday']
        cleaned_data = {key: form.cleaned_data[key] for key in event_required_keys}
        event = Event.objects.create(**cleaned_data)
        cleaned_data['id'] = event.id
        return JsonResponse(
            status=201,
            data=cleaned_data,
        )

    def get(self, request, *args, **kwargs):
        try:
            start = make_aware(datetime.datetime.strptime(request.GET['start'], "%Y-%m-%d"))
            end = make_aware(datetime.datetime.strptime(request.GET['end'], "%Y-%m-%d"))

            if end < start:
                raise ValueError

            data = Event.date_related_objects.monthly_event(start, end)

            parsed_data = get_data_from_db(data)

            if not parsed_data:
                return HttpResponse(
                    status=HTTPStatus.NO_CONTENT,
                    content=json.dumps({'error': 'there is no content!'}),
                    content_type="application/json",
                )

        except Event.DoesNotExist:
            raise Http404('Monthly data you requested does not exist.')

        except (ValueError, KeyError):
            return HttpResponseBadRequest(
                content=json.dumps({'error': 'bad request!'}),
                content_type="application/json",
            )

        else:
            return HttpResponse(
                content=json.dumps(parsed_data),
                content_type="application/json",
            )


class RetrieveDailyEvent(mixin.LoginRequiredMixin,
                         mixin.PermissionRequiredMixin,
                         View):
    """
    특정 날짜에 해당하는 이벤트를 가지고 오는 뷰
    """
    permission_required = 'schedule.view_event'

    def get(self, request, *args, **kwargs):
        try:
            pull_out_data = re.compile(r'\d{4}-\d{2}-\d{2}')
            match_obj = pull_out_data.findall(str(request))

            start_date, end_date = [make_aware(datetime.datetime.strptime(parse_datetime, "%Y-%m-%d"))
                                    for parse_datetime in match_obj]

            year, month, day = [kwargs.get(i) for i in kwargs]
            target_date = make_aware(datetime.datetime(year, month, day))

            data = Event.date_related_objects.daily_event(
                start_date, end_date, target_date
            )

            parsed_data = get_data_from_db(data)

            if not parsed_data:
                raise Http404('Daily data you requested does not exist.')

        except ValueError:
            return HttpResponseBadRequest(
                content=json.dumps({'error': 'bad request!'}),
                content_type="application/json",
            )

        except Event.DoesNotExist:
            raise Http404('Daily data you requested does not exist.')

        else:
            return HttpResponse(
                content=json.dumps(parsed_data),
                content_type="application/json",
            )
