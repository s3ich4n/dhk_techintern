from django.contrib import admin

# Register your models here.
from schedule.models import Event

admin.site.register(Event)
