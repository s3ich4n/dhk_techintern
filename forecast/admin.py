from django.contrib import admin

from forecast.models import Forecast, Region

admin.site.register(Forecast)
admin.site.register(Region)
