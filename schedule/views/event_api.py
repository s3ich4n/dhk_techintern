from http import HTTPStatus

from django.http import JsonResponse
from django.utils import timezone
from django.views import generic

from account import mixin
from schedule.models import Event


class EventAPIView(mixin.LoginRequiredMixin,
                   mixin.PermissionRequiredMixin,
                   generic.View):
    permission_required = {
        'GET': ('schedule.view_event',),
        'DELETE': ('schedule.delete_event',),
    }

    def get(self, request, *args, **kwargs):

        try:
            event = Event.objects.get(pk=self.kwargs['id'], deleted__isnull=True)
        except Event.DoesNotExist:
            # 존재하지 않는 id로 요청시 에러반환
            return JsonResponse(
                status=HTTPStatus.NOT_FOUND,
                data={'message': '해당 id 값의 이벤트가 존재하지 않습니다.'},
            )

        event_dict = {
            'title': event.title,
            'start': event.start_at,
            'end': event.end_at,
            'id': event.id,
            'description': event.description,
            'author': event.author,
            'category': event.category,
            'is_allday': event.is_allday,
        }

        # 정상적 요청
        return JsonResponse(
            status=HTTPStatus.OK,
            data=event_dict,
        )

    def delete(self, request, *args, **kwargs):

        try:
            event = Event.objects.get(id=kwargs['id'], deleted__isnull=True)

            if event.is_ended_event:
                return JsonResponse(
                    status=HTTPStatus.FORBIDDEN,
                    data={"message": "일정이 종료된 데이터는 삭제할수 없습니다."},
                )
            else:
                Event.objects.filter(id=kwargs['id']).update(deleted=timezone.now())

        except Event.DoesNotExist:
            return JsonResponse(
                status=HTTPStatus.NOT_FOUND,
                data={"message": "이미 삭제된 데이터 입니다."},

            )

        return JsonResponse(
            status=HTTPStatus.OK,
            data={"message": "요청이 정상적으로 처리되었습니다."},
        )
