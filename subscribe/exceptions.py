class WrongEmailDomainException(Exception):
    def __init__(self):
        invalid_mail_message = "이메일 주소가 올바르지 않습니다."
