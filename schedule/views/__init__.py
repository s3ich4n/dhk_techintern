from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView

from schedule.views import api_retrieve_all_month_data
from schedule.views.event_update_view import EventUpdateView
from subscribe.models import Subscriber


class CalenderTemplateView(TemplateView):
    template_name = 'schedule/calendar_index.html'

    def get_context_data(self, user, **kwargs):
        context = super().get_context_data(**kwargs)
        current_time = timezone.now()
        context['year'] = current_time.year
        context['month'] = current_time.month
        context['day'] = current_time.day
        context['DOMAIN'] = '@' + settings.DOMAIN

        if user.is_authenticated:
            try:
                user_informations = Subscriber.objects.get(subscriber=user)
            except Subscriber.DoesNotExist:
                context['is_subscribed'] = False
            else:
                context['is_subscribed'] = user_informations.is_subscribed
                context['subscribing_email'] = user_informations.subscribing_email
        else:
            context['is_subscribed'] = False

        return context

    def get(self, request, *args, **kwargs):
        return render(request=request,
                      template_name=self.template_name,
                      context=self.get_context_data(request.user))
