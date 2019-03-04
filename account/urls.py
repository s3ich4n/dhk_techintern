from django.urls import path

import configuration
from account import views
from account.tests.util import account_unittest_view

urlpatterns = [

    path('logout/', views.LogoutView.as_view(), name='logout_api'),

]

# 단위 테스트에서만 사용되는 api
if getattr(configuration.settings, 'UNIT_TEST', 'False'):
    urlpatterns += [
        path('test-mixin/', account_unittest_view.MixinTestView.as_view(), name='mixin_test_api'),

    ]
