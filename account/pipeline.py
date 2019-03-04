from django.contrib.auth.models import Permission

from account import util
from account.models import UserType
from subscribe.models import Subscriber


def add_permissions_user(strategy, backend,
                         details, *args, **kwargs):
    email = details['email']
    users = strategy.storage.user.get_users_by_email(email)
    if kwargs['is_new']:
        for permcode in util.get_permission_list(
                user_type=UserType.NORMAL_USER):
            users[0].user_permissions.add(
                Permission.objects.get(codename=permcode)
            )
        users[0].save()

        Subscriber.objects.create(
            subscriber=users[0],
            is_subscribed=False,
        )

    return {'user': users[0]}
