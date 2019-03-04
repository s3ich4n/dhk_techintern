from enum import Enum


class WeatherEnum(Enum):
    SUN = '맑음'
    CLOUDS = '흐림'
    FOG = '안개'
    THUNDERSTORM = '천둥'
    SNOWFLAKE = '눈'
    CLOUD_HAIL = '우박'
    RAINDROPS = '비'
    SUN_DUST = '황사'

    SHOWER = '소나기'
    BOLT = '번개'
    THUNDER_STROKE = '낙뢰'
    THUNDER_RAIN = '뇌우'
    SMOG = '연무'
    THIN_FOG = '박무'
    CLOUD = '구름'

    UNKNOWN = '알수없음'


def _cleanse_weather_text(weather_text):
    if weather_text == "":
        return '맑음'
    daily_weather = set()
    for w_member in WeatherEnum.__members__.values():
        if w_member.value in weather_text:
            if w_member.value == WeatherEnum.SHOWER.value:
                daily_weather.add(WeatherEnum.RAINDROPS.value)
            elif w_member.value in [
                WeatherEnum.THUNDER_RAIN.value,
                WeatherEnum.THUNDER_STROKE.value,
                WeatherEnum.BOLT.value,
            ]:
                daily_weather.add(WeatherEnum.THUNDERSTORM.value)
            elif w_member.value in [
                WeatherEnum.SMOG.value,
                WeatherEnum.THIN_FOG.value,
            ]:
                daily_weather.add(WeatherEnum.FOG.value)
            elif w_member.value == WeatherEnum.CLOUD.value:
                daily_weather.add(WeatherEnum.CLOUDS.value)
            else:
                daily_weather.add(w_member.value)
    cleaned_weather = "/".join(daily_weather) if daily_weather else WeatherEnum.UNKNOWN.value
    return cleaned_weather
