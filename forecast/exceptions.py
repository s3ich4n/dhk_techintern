from http import HTTPStatus


class ForecastServerResponseException(Exception):
    def __init__(self, status_code, server_name, message=None):
        self.status_code = status_code
        self.server_name = server_name
        self.message = message or f'{self.server_name} responses {self.status_code}.'

    def __str__(self):
        return self.message


def handle_invalid_server_response(response, server_name):
    if response.status_code != HTTPStatus.OK:
        raise ForecastServerResponseException(
            server_name=server_name,
            status_code=HTTPStatus(response.status_code).phrase
        )


class InvalidParameterException(Exception):
    def __init__(self, message=None):
        self.message = message or '유효하지 않은 날짜입니다.'

    def __str__(self):
        return self.message
