from django.urls import path

from forecast.views import get_forecasts


app_name = 'forecast'
urlpatterns = [
    path('', get_forecasts, name='retrieve-forecasts'),
]
