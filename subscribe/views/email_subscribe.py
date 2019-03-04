from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.generic.base import View

from account import mixin
from subscribe.models import Subscriber

User = get_user_model()


class EmailSubscribe(mixin.LoginRequiredMixin, View):

    model = User, Subscriber

    def post(self, request, *args, **kwargs):
        email_param = request.POST.get('email')

        try:
            validate_email(email_param.lower())

        except (ValidationError, AttributeError):
            return JsonResponse(
                status=HTTPStatus.BAD_REQUEST,
                data={'message': '유효한 이메일 주소를 입력해 주세요.'},
            )

        email_param = email_param.lower()

        query_affected_rows = (Subscriber.objects
                               .filter(subscriber=request.user)
                               .update(is_subscribed=True, subscribing_email=email_param))

        if not query_affected_rows:
            return JsonResponse(
                status=HTTPStatus.CONFLICT,
                data={'message': '이미 구독중인 계정입니다.'},
            )

        else:
            return JsonResponse(
                status=HTTPStatus.CREATED,
                data={'email': email_param},
            )

    def delete(self, request, *args, **kwargs):
        (Subscriber.objects
         .filter(subscriber__email=request.user.email)
         .update(is_subscribed=False, subscribing_email=''))

        return JsonResponse(
            status=HTTPStatus.OK,
            data={"message": "구독해지가 정상적으로 완료되었습니다."}
        )
