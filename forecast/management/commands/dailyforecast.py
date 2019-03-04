from django.core.management.base import BaseCommand, CommandError

from forecast.modules.daily_info import get_daily_weather_by_region, update_or_create_daily_forecast
from forecast.models import Region


class Command(BaseCommand):
    help = '오늘날씨를 요청하고 DB에 저장합니다.'

    def handle(self, *args, **options):
        regions = Region.objects.all()
        for region in regions:
            try:
                update_or_create_daily_forecast(get_daily_weather_by_region(region))
            except Exception as exp:
                raise CommandError(f'{exp.__class__.__name__}:::{exp}')
