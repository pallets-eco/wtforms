#!/usr/bin/env python
import json

from unittest import TestCase
from wtforms.ext.tornado import TornadoInputWrapper
from wtforms.ext.tornado.i18n import Form
from wtforms.fields import Field, TextField, _unset_value
from wtforms.validators import Required
from tornado import locale, web, testing
from tornado.httpserver import HTTPRequest


class SneakyField(Field):
    def __init__(self, sneaky_callable, *args, **kwargs):
        super(SneakyField, self).__init__(*args, **kwargs)
        self.sneaky_callable = sneaky_callable

    def process(self, formdata, data=_unset_value):
        self.sneaky_callable(formdata)


class TornadoWrapperTest(TestCase):
    def setUp(self):
        self.test_values = HTTPRequest('GET', 'http://localhost?a=Apple&b=Banana&a=Cherry')
        self.empty_mdict = TornadoInputWrapper({})
        self.filled_mdict = TornadoInputWrapper(self.test_values.arguments)

    def test_automatic_wrapping(self):
        def _check(formdata):
            self.assertTrue(isinstance(formdata, TornadoInputWrapper))

        form = Form({'a': SneakyField(_check)})
        form.process(self.filled_mdict)

    def test_empty(self):
        formdata = TornadoInputWrapper(self.empty_mdict)
        self.assertFalse(formdata)
        self.assertEqual(len(formdata), 0)
        self.assertEqual(list(formdata), [])
        self.assertEqual(formdata.getlist('fake'), [])

    def test_filled(self):
        formdata = TornadoInputWrapper(self.filled_mdict)
        self.assertTrue(formdata)
        self.assertEqual(len(formdata), 2)
        self.assertEqual(list(formdata), ['a', 'b'])
        self.assertTrue('b' in formdata)
        self.assertTrue('fake' not in formdata)
        self.assertEqual(formdata.getlist('a'), ['Apple', 'Cherry'])
        self.assertEqual(formdata.getlist('b'), ['Banana'])
        self.assertEqual(formdata.getlist('fake'), [])


class SearchForm(Form):

    search = TextField(validators=[Required('Search field is required')])


class DummyHandler(web.RequestHandler):

    def get_user_locale(self):
        return locale.get(self.get_argument('locale', 'en_US'))

    def get(self):
        form = SearchForm(self.request.arguments, locale_code=self.locale.code)
        if bool(self.get_argument('label', False)):
            self.finish({'label': form.search.label.text})
        else:
            if form.validate():
                self.finish(form.data)
            else:
                self.set_status(500)
                self.finish(form.errors)

if type('') is not type(b''):
    def u(s):
        return s
    bytes_type = bytes
else:
    def u(s):
        return s.decode('unicode_escape')
    bytes_type = str


def utf8(value):
    if isinstance(value, (bytes_type, type(None))):
        return value
    return value.encode("utf-8")


class TornadoApplicationTest(testing.AsyncHTTPTestCase,
                             testing.LogTrapTestCase):

    def setUp(self):
        super(TornadoApplicationTest, self).setUp()
        locale.load_translations('tests/ext_tornado/translations')

    def get_app(self):
        return web.Application([('/', DummyHandler)])

    def test_successful_form(self):
        response = self.fetch('/?search=wtforms&page=2')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(body, {'search': 'wtforms'})

    def test_wrong_form(self):
        response = self.fetch('/?fake=wtforms')
        body = json.loads(response.body)
        self.assertEqual(response.code, 500)
        self.assertEqual(body, {'search': ['Search field is required']})

    def test_translations_default(self):
        response = self.fetch('/?label=True&search=wtforms')
        body = json.loads(response.body)
        self.assertEqual(body, {'label': 'Search'})

    def test_translations_en(self):
        response = self.fetch('/?locale=en_US&label=True&search=wtforms')
        body = json.loads(response.body)
        self.assertEqual(body, {'label': 'Search'})

    def test_translations_es(self):
        response = self.fetch('/?locale=es_ES&label=True&search=wtforms')
        body = json.loads(response.body)
        self.assertEqual(body['label'], u('B\xfasqueda'))
        self.assertEqual(utf8(body['label']), b'B\xc3\xbasqueda')

if __name__ == '__main__':
    from unittest import main
    main()
