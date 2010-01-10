#!/usr/bin/env python
from unittest import TestCase
from wtforms.form import BaseForm, WebobInputWrapper
from wtforms.fields import Field, _unset_value 

try:
    from webob.multidict import MultiDict
    has_webob = True
except ImportError:
    has_webob = False


class MockMultiDict(object):
    def __init__(self, tuples):
        self.tuples = tuples

    def __len__(self):
        return len(self.tuples)

    def __iter__(self):
        for k, _ in self.tuples:
            yield k

    def __contains__(self, key):
        for k, _ in self.tuples:
            if k == key:
                return True
        return False

    def getall(self, key):
        result = []
        for k, v in self.tuples:
            if key == k:
                result.append(v)
        return result


class SneakyField(Field):
    def __init__(self, sneaky_callable, *args, **kwargs):
        super(SneakyField, self).__init__(*args, **kwargs)
        self.sneaky_callable = sneaky_callable

    def process(self, formdata, data=_unset_value): 
        self.sneaky_callable(formdata)


class WebobWrapperTest(TestCase):
    def setUp(self):
        w_cls = has_webob and MultiDict or MockMultiDict

        self.test_values = [('a', 'Apple'), ('b', 'Banana'), ('a', 'Cherry')]
        self.empty_mdict = w_cls([])
        self.filled_mdict = w_cls(self.test_values)

    def test_automatic_wrapping(self):
        def _check(formdata):
            self.assert_(isinstance(formdata, WebobInputWrapper))

        form = BaseForm({'a': SneakyField(_check)})
        form.process(self.filled_mdict)

    def test_empty(self):
        formdata = WebobInputWrapper(self.empty_mdict)
        self.assert_(not formdata)
        self.assertEqual(len(formdata), 0)
        self.assertEqual(list(formdata), [])
        self.assertEqual(formdata.getlist('fake'), [])

    def test_filled(self):
        formdata = WebobInputWrapper(self.filled_mdict)
        self.assert_(formdata)
        self.assertEqual(len(formdata), 3)
        self.assertEqual(list(formdata), ['a','b','a'])
        self.assert_('b' in formdata)
        self.assert_('fake' not in formdata)
        self.assertEqual(formdata.getlist('a'), ['Apple', 'Cherry'])
        self.assertEqual(formdata.getlist('b'), ['Banana'])
        self.assertEqual(formdata.getlist('fake'), [])


if __name__ == '__main__':
    from unittest import main
    main()

