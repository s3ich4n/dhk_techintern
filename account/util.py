import json

from django.conf import settings


def get_permission_list(user_type):
    with open(settings.BASE_DIR + '/account/user_permission_list.json') as json_data:
        data = json.load(json_data)
        return data[user_type.value]
