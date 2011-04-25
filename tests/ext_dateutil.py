#!/usr/bin/env python
from datetime import datetime, date
from unittest import TestCase

from wtforms.form import Form
from wtforms.ext.dateutil.fields import DateTimeField, DateField


class DummyPostData(dict):
    def getlist(self, key):
        v = self[key]
        if not isinstance(v, (list, tuple)):
            v = [v]
        return v

class DateutilTest(TestCase):
    class F(Form):
        a = DateTimeField()
        b = DateField(default=lambda: date(2004, 9, 12))
        c = DateField(parse_kwargs=dict(yearfirst=True, dayfirst=False))

    def test_form_input(self):
        f = self.F(DummyPostData(a='2008/09/12 4:17 PM', b='04/05/06', c='04/05/06'))
        self.assertEqual(f.a.data, datetime(2008, 9, 12, 16, 17))
        self.assertEqual(f.a._value(), '2008/09/12 4:17 PM')
        self.assertEqual(f.b.data, date(2006, 4, 5))
        self.assertEqual(f.c.data, date(2004, 5, 6))
        self.assert_(f.validate())
        f = self.F(DummyPostData(a='Grok Grarg Rawr'))
        self.assert_(not f.validate())

    def test_blank_input(self):
        f = self.F(DummyPostData(a='', b=''))
        self.assertEqual(f.a.data, None)
        self.assertEqual(f.b.data, None)
        self.assert_(not f.validate())

    def test_defaults_display(self):
        f = self.F(a=datetime(2001, 11, 15))
        self.assertEqual(f.a.data, datetime(2001, 11, 15))
        self.assertEqual(f.a._value(), u'2001-11-15 00:00')
        self.assertEqual(f.b.data, date(2004, 9, 12))
        self.assertEqual(f.b._value(), u'2004-09-12')
        self.assertEqual(f.c.data, None)
        self.assert_(f.validate())

    def test_render(self):
        f = self.F()
        self.assertEqual(f.b(), ur'<input id="b" name="b" type="text" value="2004-09-12">')


if __name__ == '__main__':
    from unittest import main
    main()
