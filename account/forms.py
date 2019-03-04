from django import forms
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    retype_password = forms.CharField(
        widget=forms.PasswordInput,
        strip=False,
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'retype_password', 'email', 'first_name')

    @staticmethod
    def cleanse_text(text):
        return text.replace('\n', '').strip()

    def clean_username(self):
        username = self.cleaned_data.get('username')
        cleaned_username = self.cleanse_text(username)
        if cleaned_username == '':
            raise forms.ValidationError('필수 항목입니다.')
        return cleaned_username

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        cleaned_first_name = self.cleanse_text(first_name)
        if cleaned_first_name == '':
            raise forms.ValidationError('필수 항목입니다.')
        return cleaned_first_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        cleaned_email = self.cleanse_text(email)
        if not cleaned_email.endswith(settings.DOMAIN):
            raise forms.ValidationError('사내 계정이 아닙니다')
        return cleaned_email

    def clean_password(self):
        cleaned_password = self.cleaned_data.get('password')
        if cleaned_password == '':
            raise forms.ValidationError('필수 항목입니다.')
        elif len(cleaned_password) < 8:
            raise forms.ValidationError('8자 이상이여야합니다.')
        return cleaned_password

    def clean_retype_password(self):
        retype_password = self.cleaned_data.get('retype_password')
        password = self.cleaned_data.get('password')
        if password and retype_password and retype_password != password:
            raise forms.ValidationError('비밀번호가 일치하지 않습니다')
        return retype_password
