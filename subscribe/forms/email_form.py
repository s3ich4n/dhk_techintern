from django import forms
from django.core.validators import validate_email

from subscribe.models import Subscriber


class EmailSubscribeForm(forms.ModelForm):

    def clean_email(self):
        try:
            email = self.cleaned_data.get('email')
            cleaned_email = validate_email(email)
        except validate_email.ValidationError:
            forms.ValidationError('error!')
        else:
            return cleaned_email

    class Meta:
        model = Subscriber
        fields = [
            'subscribing_email',
        ]
