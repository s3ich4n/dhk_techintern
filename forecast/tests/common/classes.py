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


class RegionEnum(Enum):
    SEOUL = '서울'
    DAEGEON = '대전'
    DAEGU = '대구'
    BUSAN = '부산'
