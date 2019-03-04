from http import HTTPStatus

from django.http import JsonResponse
from django.views import generic

from account import mixin


class MixinTestView(mixin.LoginRequiredMixin,
                    mixin.PermissionRequiredMixin,
                    generic.View):
    permission_required = {
        'GET': ('schedule.view_event',),
        'POST': ('schedule.add_event',),
        "PUT": ('schedule.change_event',),
        'DELETE': ('schedule.delete_event',),
    }

    def get(self, request, *args, **kwargs):
        return JsonResponse(
            status=HTTPStatus.OK,
            data={
                "message": "테스트 성공"
            }
        )
