from http import HTTPStatus
from json import loads

from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.views.generic import UpdateView

from account import mixin
from schedule.exceptions import AccessAlreadyEndedEventException
from schedule.forms import EventForm
from schedule.models import Event


class EventUpdateView(mixin.LoginRequiredMixin,
                      mixin.PermissionRequiredMixin,
                      UpdateView):
    object = None
    model = Event
    form_class = EventForm

    permission_required = {
        "PUT": ('schedule.change_event',),
    }

    def get_object(self, queryset=None):
        present_time = timezone.now()
        try:
            event = self.model.get_not_ended_event(
                event_id=self.kwargs['id'],
                present_time=present_time,
            )
        except self.model.DoesNotExist as not_exist_err:
            raise not_exist_err
        except AccessAlreadyEndedEventException as access_denied_err:
            raise access_denied_err
        return event

    def put(self, *args, **kwargs):
        try:
            updated_event = self.get_object()
        except self.model.DoesNotExist:
            raise Http404()
        except AccessAlreadyEndedEventException:
            return HttpResponseForbidden('접근할 수 없는 이벤트입니다.')
        else:
            requested_data = loads(self.request.body)
            event_form = self.form_class(
                data=requested_data,
                instance=updated_event,
            )
            if not event_form.is_valid():
                if event_form.has_error('__all__'):
                    event_form.errors['all'] = event_form.errors.pop('__all__')
                response = JsonResponse({
                    'error': event_form.errors.as_json(),
                })
                response.status_code = HTTPStatus.BAD_REQUEST
                return response
            event_form.save()
            response = JsonResponse(event_form.cleaned_data)
            response.status_code = HTTPStatus.OK
            return response
