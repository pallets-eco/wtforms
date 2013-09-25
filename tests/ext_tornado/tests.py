#!/usr/bin/env python
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
            self.finish(form.search.label.text)
        else:
            if form.validate():
                self.finish(form.data)
            else:
                self.set_status(500)
                self.finish(form.errors)


class TornadoApplicationTest(testing.AsyncHTTPTestCase,
                             testing.LogTrapTestCase):

    def setUp(self):
        super(TornadoApplicationTest, self).setUp()
        locale.load_translations('tests/ext_tornado/translations')

    def get_app(self):
        return web.Application([('/', DummyHandler)])

    def test_successful_form(self):
        response = self.fetch('/?search=wtforms&page=2')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, '{"search": "wtforms"}')

    def test_wrong_form(self):
        response = self.fetch('/?fake=wtforms')
        self.assertEqual(response.code, 500)
        self.assertEqual(response.body, '{"search": ["Search field is required"]}')

    def test_translations_default(self):
        response = self.fetch('/?label=True&search=wtforms')
        self.assertEqual(response.body, 'Search')

    def test_translations_en(self):
        response = self.fetch('/?locale=en_US&label=True&search=wtforms')
        self.assertEqual(response.body, 'Search')

    def test_translations_es(self):
        response = self.fetch('/?locale=es_ES&label=True&search=wtforms')
        self.assertEqual(response.body, b'B\xc3\xbasqueda')

if __name__ == '__main__':
    from unittest import main
    main()
