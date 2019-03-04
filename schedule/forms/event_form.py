from datetime import datetime, timedelta
from distutils.util import strtobool

from django import forms

from schedule.models import Event

START_AT_ALLDAY_TIME = END_AT_DEFAULT_TIME = '00:00'
START_AT_DEFAULT_TIME = '17:00'


class EventForm(forms.ModelForm):
    # TODO : author에 대한 clean 메서드 작성.
    class Meta:
        model = Event
        fields = [
            'title',
            'category',
            'start_at',
            'end_at',
            'description',
            'author',
            'is_allday',
        ]

    category_choices = [
        '사내',
        '사외',
    ]

    @staticmethod
    def cleanse_text(text):
        return text.replace('\n', '').strip()

    @staticmethod
    def cleanse_time(time):
        return time.replace(second=0, microsecond=0)

    def full_clean(self):
        is_allday = self.data.get('is_allday')
        if isinstance(is_allday, str):
            is_allday = strtobool(is_allday)
        start_at_type = self.data.get('start_at_type')
        end_at_type = self.data.get('end_at_type')

        if (start_at_type and end_at_type) is not None:
            self.pre_clean_datetime(is_allday, start_at_type, end_at_type)
        return super().full_clean()

    def pre_clean_datetime(self, is_allday, start_at_type, end_at_type):
        if start_at_type == '' or start_at_type == 'time':
            return None
        elif is_allday:
            self.init_datetime_for_allday(end_at_type)
        elif start_at_type == 'date':
            self.data['start_at'] = '{} {}'.format(self.data['start_at'], START_AT_DEFAULT_TIME)
        self.pre_clean_end_at()

    def init_datetime_for_allday(self, end_at_type):
        start_at = self.data['start_at']
        end_at = self.data['end_at']
        start_at_date = datetime.strptime(start_at.split(' ')[0], '%Y-%m-%d').date()
        self.data['start_at'] = '{} {}'.format(start_at_date, START_AT_ALLDAY_TIME)
        if end_at_type == '' or end_at_type == 'time':
            end_at_date = start_at_date + timedelta(days=1)
            self.data['end_at'] = '{} {}'.format(end_at_date, END_AT_DEFAULT_TIME)
            self.data['end_at_type'] = 'datetime'
        elif end_at_type == 'date' or end_at_type == 'datetime':
            end_at_date = datetime.strptime(end_at.split(' ')[0], '%Y-%m-%d').date()
            self.data['end_at'] = end_at_date.isoformat()
            self.data['end_at_type'] = 'date'

    def pre_clean_end_at(self):
        end_at_type = self.data['end_at_type']
        start_at = self.data['start_at']
        start_at_date = datetime.strptime(start_at, '%Y-%m-%d %H:%M').date()
        end_at = self.data['end_at']
        if end_at_type == '':
            self.data['end_at'] = start_at
        elif end_at_type == 'date':
            end_at_date = datetime.strptime(end_at, '%Y-%m-%d').date() + timedelta(days=1)
            self.data['end_at'] = '{} {}'.format(end_at_date, END_AT_DEFAULT_TIME)
        elif end_at_type == 'time':
            self.data['end_at'] = '{} {}'.format(start_at_date, end_at)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        cleaned_title = self.cleanse_text(title)
        if cleaned_title == '':
            raise forms.ValidationError('필수 항목입니다.')
        return cleaned_title

    def clean_start_at(self):
        start_at = self.cleaned_data.get('start_at')
        cleaned_start_at = self.cleanse_time(start_at)
        return cleaned_start_at

    def clean_end_at(self):
        end_at = self.cleaned_data.get('end_at')
        cleaned_end_at = self.cleanse_time(end_at)
        return cleaned_end_at

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if category not in self.category_choices:
            raise forms.ValidationError('이벤트 분류는 사내/사외에서만 선택가능합니다.')
        return category

    def clean_description(self):
        # description은 blank=True 옵션을 가지므로 빈 문자열일 경우 ValidationError가 발생하지 않습니다.
        description = self.cleaned_data.get('description')
        if description is not None:
            cleaned_description = self.cleanse_text(description)
            return cleaned_description
        return description

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('start_at') or not cleaned_data.get('end_at'):
            return None
        if cleaned_data.get('start_at') > cleaned_data.get('end_at'):
            raise forms.ValidationError('시작시간이 종료시간보다 이릅니다. 시작/종료시간을 다시 입력하세요.')
        return cleaned_data
