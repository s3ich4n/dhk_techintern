from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string


def logged_in_account_maker(self, email_case):
    User = get_user_model()

    user = User.objects.create_user(
        username=get_random_string(length=16),
        password=self.password,
        email=email_case,
    )
    self.client.login(
        username=user.username,
        password=self.password,
    )

    return user
