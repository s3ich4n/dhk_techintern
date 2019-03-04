from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from schedule.forms import EventForm


class EventFormTest(TestCase):
    # TODO : clean_<필드이름>에 대한 테스트케이스 작성.
    # TODO : author에 대한 테스트케이스 작성.

    def setUp(self):
        self.valid_event = {
            'title': '유효한 타이틀',
            'category': '사내',
            'start_at': timezone.now(),
            'end_at': timezone.now(),
            'description': '유효한 상세설명',
            'author': 'kde6260'
        }

    def _assertEachFieldIsNone(self, form, fields):
        for field in fields:
            self.assertIsNone(form.errors.get(field))

    def test_event_form_should_be_invalid_when_taking_empty_title(self):
        # Given
        event = self.valid_event
        # title을 빈 문자열로 변경.
        event.update({'title': ''})

        # When
        form = EventForm(data=event)

        # Then
        # 폼은 유효하지 않아야 함.
        self.assertFalse(form.is_valid())
        # 빈 문자열의 title에 관한 메세지만이 title 에러리스트에 있어야 함.
        self.assertListEqual(form.errors.get('title'), [
            '필수 항목입니다.',
        ])
        # title만이 유효하지 않은 필드이므로 이를 제외한 필드의 에러메세지는 없어야 함.
        self._assertEachFieldIsNone(
            form=form,
            fields=[
                'category',
                'start_at',
                'end_at',
                'description',
                'author',
                '__all__',
            ])

    def test_event_form_should_be_invalid_when_taking_title_whose_length_is_more_than_100(self):
        # Given
        event = self.valid_event
        # title을 101자 길이의 문자열로 변경.
        event.update({'title': 'A' * 101})

        # When
        form = EventForm(data=event)

        # Then
        # 폼은 유효하지 않아야 함.
        self.assertFalse(form.is_valid())
        # 100자 길이를 초과한 title에 관한 메세지만이 에러리스트에 있어야 함.
        self.assertListEqual(form.errors.get('title'), [
            '이 값이 최대 100 개의 글자인지 확인하세요(입력값 101 자).',
        ])
        # title만이 유효하지 않은 필드이므로 이를 제외한 필드의 에러메세지는 없어야 함.
        self._assertEachFieldIsNone(
            form=form,
            fields=[
                'category',
                'start_at',
                'end_at',
                'description',
                'author',
                '__all__',
            ])

    def test_event_form_should_be_invalid_when_taking_empty_category(self):
        # Given
        event = self.valid_event
        # category를 빈 문자열로 변경.
        event.update({'category': ''})

        # When
        form = EventForm(data=event)

        # Then
        # 폼은 유효하지 않아야 함.
        self.assertFalse(form.is_valid())
        # 빈 문자열의 category에 대한 에러메세지만이 리스트에 있어야 함.
        self.assertListEqual(form.errors.get('category'), [
            '필수 항목입니다.',
        ])
        # category만이 유효하지 않은 필드이므로 이를 제외한 필드의 에러메세지는 없어야 함.
        self._assertEachFieldIsNone(
            form=form,
            fields=[
                'title',
                'start_at',
                'end_at',
                'description',
                'author',
                '__all__',
            ])

    def test_event_form_should_be_invalid_when_taking_category_which_is_neither_in_firm_nor_outside_firm(self):
        # Given
        event = self.valid_event
        # category를 '사내' 또는 '사외'가 아닌 값으로 변경.
        event.update({'category': '사내/사외로 분류될 수 없는 카테고리'})

        # When
        form = EventForm(data=event)

        # Then
        # 폼은 유효하지 않아야 함.
        self.assertFalse(form.is_valid())
        # category가 '사내' 또는 '사외' 이외의 값을 갖는 것에 대한 에러메세지만이 리스트에 있어야 함.
        self.assertListEqual(form.errors.get('category'), [
            '이벤트 분류는 사내/사외에서만 선택가능합니다.',
        ])
        # category만이 유효하지 않은 필드이므로 이를 제외한 필드의 에러메세지는 없어야 함.
        self._assertEachFieldIsNone(
            form=form,
            fields=[
                'title',
                'start_at',
                'end_at',
                'description',
                'author',
                '__all__',
            ])

    def test_event_form_should_be_invalid_when_taking_start_at_which_has_invalid_format_of_datetime(self):
        # Given
        event = self.valid_event
        # 이벤트 시작시간을 datetime 포맷에 맞지 않는 값으로 변경.
        event.update({'start_at': 'datetime으로 변환될 수 없는 값'})

        # When
        form = EventForm(data=event)

        # Then
        # 폼은 유효하지 않아야 함.
        self.assertFalse(form.is_valid())
        # datetime 포맷이 아닌 것에 관한 에러메세지만이 리스트에 있어야 함.
        self.assertListEqual(form.errors.get('start_at'), [
            '올바른 날짜/시각을 입력하세요.',
        ])

        # start_at만이 유효하지 않은 필드이므로 이를 제외한 필드의 에러메세지는 없어야 함.
        self._assertEachFieldIsNone(
            form=form,
            fields=[
                'title',
                'category',
                'end_at',
                'description',
                'author',
                '__all__',
            ])

    def test_event_form_should_be_invalid_when_taking_end_at_which_has_invalid_format_of_datetime(self):
        # Given
        event = self.valid_event
        # 이벤트 종료시간을 datetime 포맷에 맞지 않는 값으로 변경.
        event.update({'end_at': 'datetime으로 변환될 수 없는 값'})

        # When
        form = EventForm(data=event)

        # Then
        # 폼은 유효하지 않아야 함.
        self.assertFalse(form.is_valid())
        # datetime 포맷이 아닌 것에 관한 에러메세지만이 리스트에 있어야 함.
        self.assertListEqual(form.errors.get('end_at'), [
            '올바른 날짜/시각을 입력하세요.',
        ])
        # end_at만이 유효하지 않은 필드이므로 이를 제외한 필드의 에러메세지는 없어야 함.
        self._assertEachFieldIsNone(
            form=form,
            fields=[
                'title',
                'category',
                'start_at',
                'description',
                'author',
                '__all__',
            ])

    def test_event_form_should_be_invalid_when_taking_start_at_later_than_end_at(self):
        # Given
        event = self.valid_event
        # 이벤트의 시작시간을 종료시간보다 늦은 시간으로 변경.
        event.update({'start_at': event.get('end_at') + timedelta(minutes=1)})

        # When
        form = EventForm(data=event)

        # Then
        # 폼은 유효하지 않아야 함.
        self.assertFalse(form.is_valid())
        # start_at과 end_at(다수의 필드)에 관한 에러이므로 __all__의 에러리스트에 에러메세지가 있어야 함.
        self.assertListEqual(form.errors.get('__all__'), [
            '시작시간이 종료시간보다 이릅니다. 시작/종료시간을 다시 입력하세요.',
        ])
        # 각 필드의 에러메세지는 없어야 함.
        self._assertEachFieldIsNone(
            form=form,
            fields=[
                'title',
                'category',
                'start_at',
                'end_at',
                'description',
                'author',
            ])

    def test_event_form_should_be_invalid_when_taking_description_whose_length_is_more_than_300(self):
        # Given
        event = self.valid_event
        # description의 길이가 301로 변경됨.
        event.update({'description': 'A' * 301})

        # When
        form = EventForm(data=event)

        # Then
        # 폼은 유효하지 않아야 함.
        self.assertFalse(form.is_valid())
        # description의 길이에 대한 에러메세지만이 description 에러리스트에 있어야 함.
        self.assertListEqual(form.errors.get('description'), [
            '이 값이 최대 300 개의 글자인지 확인하세요(입력값 301 자).',
        ])
        # description만이 유효하지 않은 필드이므로 이를 제외한 필드의 에러메세지는 없어야 함.
        self._assertEachFieldIsNone(
            form=form,
            fields=[
                'title',
                'category',
                'start_at',
                'end_at',
                'author',
                '__all__',
            ])

    def test_event_form_shoud_be_valid_when_taking_empty_description(self):
        # Given
        event = self.valid_event
        # description을 빈 문자열로 변경.
        event.update({'description': ''})

        # When
        form = EventForm(data=event)

        # Then
        # description은 입력하지 않아도 되는 필드이므로 빈 문자열로 들어와도 폼 유효성 검사에서 통과되어야 함.
        self.assertTrue(form.is_valid())

    def test_event_form_should_be_valid_when_taking_only_valid_fields(self):
        # Given
        # 유효한 이벤트
        event = self.valid_event

        # When
        form = EventForm(data=event)

        # Then
        # 유효한 필드만을 갖는 이벤트를 넘겨줬으므로 폼의 유효성 검사는 통과되어야 함.
        self.assertTrue(form.is_valid())
