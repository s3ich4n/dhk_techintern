from django.urls import path, include

from schedule import views
from schedule.views import api_retrieve_all_month_data
from schedule.views import event_api

app_name = 'schedule'
urlpatterns = [
    path('', views.CalenderTemplateView.as_view(), name='index'),
    path('events/<int:id>/', event_api.EventAPIView.as_view(), name='event_api'),
    path('events/<int:id>/edit/', views.EventUpdateView.as_view(), name='update-event'),
    path('events/', include([
        path('',
             api_retrieve_all_month_data.RetrieveMonthlyEvent.as_view(),
             name='api-retrieve-monthly-value'),
        path('<int:year>/<int:month>/<int:day>/',
             api_retrieve_all_month_data.RetrieveDailyEvent.as_view(),
             name='api-retrieve-daily-event'),
    ])),
]
