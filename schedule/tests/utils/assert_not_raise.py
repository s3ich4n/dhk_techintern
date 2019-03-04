from contextlib import contextmanager


class AssertNotRaise:
    @contextmanager
    def assertNotRaises(self, expected_exception, *args, **kwargs):
        try:
            yield None
        except expected_exception:
            raise AssertionError('{} raised.'.format(expected_exception.__name__))
