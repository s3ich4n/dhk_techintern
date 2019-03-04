from datetime import date

from django.core.management.base import BaseCommand, CommandError

from configuration.settings.base import GISANG_OLDEST_REFERENCE_YEAR
from forecast.modules.daily_info import update_or_create_daily_forecast
from forecast.modules.yearly_info import get_yearly_forecasts_by_region
from forecast.models import Region


class Command(BaseCommand):
    help = '지역별 연간날씨를 기상청 홈페이지에서 크롤링하여 DB에 저장합니다. 사용 예)./manage.py yearlyforecast 2018 서울'
    regions = Region.objects.all()

    @staticmethod
    def get_regions():
        return ', '.join([region.name for region in Command.regions])

    def add_arguments(self, parser):
        parser.add_argument(
            'year',
            type=int,
            help=f'날씨정보를 가져올 연도.({GISANG_OLDEST_REFERENCE_YEAR} ~ 현재연도)'
        )
        parser.add_argument(
            'region',
            type=str,
            help=f'날씨정보를 가져올 지역.({self.regions} 중 택1)',
        )

    def handle(self, *args, **options):
        input_year = options.get('year')
        present_year = date.today().year
        if input_year < GISANG_OLDEST_REFERENCE_YEAR or input_year > present_year:
            return self.stdout.write(f'입력가능한 연도: {GISANG_OLDEST_REFERENCE_YEAR} ~ {present_year}.')

        input_region = options.get('region')
        if input_region not in self.get_regions():
            return self.stdout.write(f'입력가능한 지역: {self.get_regions()}.')

        region = Region.objects.get(name=input_region)
        try:
            forecast_crawled_by_region = get_yearly_forecasts_by_region(
                region=region,
                year=input_year,
            )
        except Exception as exp:
            raise CommandError(f'{exp.__class__.__name__}:::{exp}')

        [update_or_create_daily_forecast(forecast) for forecast in forecast_crawled_by_region]
