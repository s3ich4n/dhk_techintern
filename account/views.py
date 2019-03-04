from http import HTTPStatus

from django.contrib.auth import logout
from django.http import JsonResponse
from django.views import generic


class LogoutView(generic.View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse(
            status=HTTPStatus.OK,
            data={
                "message": "로그아웃 되었습니다",
            }
        )
