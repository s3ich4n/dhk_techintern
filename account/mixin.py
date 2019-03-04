import logging
from http import HTTPStatus

from django.http import JsonResponse


class NoPermissionRequiredException(Exception):
    pass


class PermissionRequiredMixin(object):
    permission_required = {}

    def get_permission_required(self):
        try:
            self.permission_required
        except AttributeError:
            raise NoPermissionRequiredException(
                'There is no permission_required !! with View Class. can not config PermissionMixin !!'
            )

        if isinstance(self.permission_required, str):
            perms = {
                'GET': (self.permission_required,),
                'POST': (self.permission_required,),
                'PUT': (self.permission_required,),
                'DELETE': (self.permission_required,),
            }
        else:
            perms = self.permission_required
        return perms

    def has_permission(self):
        perms_dict = self.get_permission_required()

        return self.request.user.has_perms(perms_dict[self.request.method])

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            logging.info('PermissionRequiredMixin: 권한이 없습니다')
            return JsonResponse(
                status=HTTPStatus.FORBIDDEN,
                data={
                    'message': '해당요청에 권한이 없습니다',
                }
            )
        return super().dispatch(request, *args, **kwargs)


class LoginRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        logging.info('LoginRequiredMixin: 인증에 실패하였습니다')
        if not request.user.is_authenticated:
            return JsonResponse(
                status=HTTPStatus.UNAUTHORIZED,
                data={
                    'message': '인증되지 않은 사용자입니다',
                }
            )

        return super().dispatch(request, *args, **kwargs)
