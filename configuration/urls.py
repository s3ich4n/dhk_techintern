from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from schedule.views import CalenderTemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', CalenderTemplateView.as_view(), name='index_page'),

    path('schedule/', include(('schedule.urls', 'schedule'), namespace='schedule')),
    path('account/', include(('account.urls', 'account'), namespace='account')),

    # social-login
    path('social/', include('social_django.urls', namespace='social')),



    path('subscribe/', include('subscribe.urls', namespace='subscribe')),
    path('forecast/', include('forecast.urls', namespace='forecast')),
]

# 디버깅실행시 툴바로 넘어가는 설정
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),

    ]
