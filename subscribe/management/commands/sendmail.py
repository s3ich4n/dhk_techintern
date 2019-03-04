from django.core.management.base import BaseCommand

from subscribe.scripts import mail_sender, parse_holiday_data


class Command(BaseCommand):
    help = '구독자들에게 오늘의 이벤트를 전송하는 명령어 입니다.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('명령어 작동 시작'))

        if not parse_holiday_data.main():
            self.stdout.write(self.style.ERROR('오늘은 쉬는날입니다. 메시지를 보내지 않습니다.'))

        else:
            self.stdout.write(self.style.SUCCESS('전송 중입니다...'))
            mail_sender.send_mail_for_subscriber()
            self.stdout.write(self.style.SUCCESS('이메일 전송 완료.'))
