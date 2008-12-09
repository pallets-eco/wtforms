"""
    test_fields
    ~~~~~~~~~~~
    
    Unittests for bundled fields.
    
    :copyright: 2007-2008 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""

from py.test import raises
from wtforms.fields import *
from wtforms.fields import Label
from wtforms.form import Form
from datetime import datetime

class DummyPostData(dict):
    def getlist(self, key):
        return self[key]

class AttrDict(dict):
    def __getattr__(self, attr):
        return self[attr]

def test_Label():
    expected = u"""<label for="test">Caption</label>"""
    label = Label('test', u'Caption')
    assert label() == expected
    assert str(label) == expected
    assert unicode(label) == expected
    assert label('hello') == u"""<label for="test">hello</label>""" 

def test_SelectField():
    class F(Form):
        a = SelectField(choices=[('a', 'hello'), ('b','bye')], default='a')
        b = SelectField(choices=[(1, 'Item 1'), (2, 'Item 2')], checker=int)
    form = F()
    assert form.a.data == u'a'
    assert form.b.data == None
    assert form.validate() == False
    assert form.a() == u"""<select id="a" name="a"><option selected="selected" value="a">hello</option><option value="b">bye</option></select>"""
    assert form.b() == u"""<select id="b" name="b"><option value="1">Item 1</option><option value="2">Item 2</option></select>"""
    form = F(DummyPostData(b=u'2'))
    assert form.b.data == 2
    assert form.validate() == True
    form = F(obj=AttrDict(b=AttrDict(id=1)))
    assert form.b.data == 1
    assert form.validate() == True
    form.b.choices = [(3, 'false')]
    assert form.validate() == False

def test_SelectMultipleField():
    class F(Form):
        a = SelectMultipleField(choices=[('a', 'hello'), ('b','bye'), ('c', 'something')], default=('a', ))
        b = SelectMultipleField(checker=int, choices=[(1, 'A'), (2, 'B'), (3, 'C')], default=("1", "3"))
    form = F()
    assert form.a.data == ['a']
    assert form.b.data == [1, 3]
    form = F(DummyPostData(a=['a', 'c']))
    assert form.a.data == ['a', 'c']
    assert form.a() == u"""<select id="a" multiple="multiple" name="a"><option selected="selected" value="a">hello</option><option value="b">bye</option><option selected="selected" value="c">something</option></select>"""
    assert form.b.data == []
    form = F(DummyPostData(b=['1', '2']))
    assert form.b.data == [1, 2]

def test_RadioField():
    class F(Form):
        a = RadioField(choices=[('a', 'hello'), ('b','bye')], default='a')
        b = RadioField(choices=[(1, 'Item 1'), (2, 'Item 2')], checker=int)
    form = F()
    assert form.a.data == u'a'
    assert form.b.data == None
    assert form.validate() == False
    assert form.a() == u"""<ul id="a"><li><input checked="checked" id="a_0" name="a" type="radio" value="a" /> <label for="a_0">hello</label></li><li><input id="a_1" name="a" type="radio" value="b" /> <label for="a_1">bye</label></li></ul>"""
    assert form.b() == u"""<ul id="b"><li><input id="b_0" name="b" type="radio" value="1" /> <label for="b_0">Item 1</label></li><li><input id="b_1" name="b" type="radio" value="2" /> <label for="b_1">Item 2</label></li></ul>"""
    assert [unicode(x) for x in form.a] == [u'<input checked="checked" id="a_0" name="a" type="radio" value="a" />', u'<input id="a_1" name="a" type="radio" value="b" />']


def test_TextField():
    class F(Form):
        a = TextField()
    form = F()
    assert form.a.data == None
    assert form.a() == u"""<input id="a" name="a" type="text" value="" />"""
    form = F(DummyPostData(a=['hello']))
    assert form.a.data == u'hello'
    assert form.a() == u"""<input id="a" name="a" type="text" value="hello" />"""

def test_HiddenField():
    class F(Form):
        a = HiddenField(default="LE DEFAULT")
    form = F()
    assert form.a() == u"""<input id="a" name="a" type="hidden" value="LE DEFAULT" />"""

def test_TextAreaField():
    class F(Form):
        a = TextAreaField(default="LE DEFAULT")
    form = F()
    assert form.a() == u"""<textarea id="a" name="a">LE DEFAULT</textarea>"""

def test_PasswordField():
    class F(Form):
        a = PasswordField(default="LE DEFAULT")
    form = F()
    assert form.a() == u"""<input id="a" name="a" type="password" value="LE DEFAULT" />"""

def test_FileField():
    class F(Form):
        a = FileField(default="LE DEFAULT")
    form = F()
    assert form.a() == u"""<input id="a" name="a" type="file" value="LE DEFAULT" />"""

def test_IntegerField():
    class F(Form):
        a = IntegerField()
        b = IntegerField()
    form = F(DummyPostData(a=['v'], b=['-15']))
    assert form.a.data == None
    assert form.a() == u"""<input id="a" name="a" type="text" value="0" />"""
    assert form.b.data == -15
    assert form.b() == u"""<input id="b" name="b" type="text" value="-15" />"""

def test_BooleanField():
    class BoringForm(Form):
        bool1  = BooleanField()
        bool2  = BooleanField(default=True)
    obj = AttrDict(bool1=None, bool2=True)
    # Test with no post data to make sure defaults work
    form = BoringForm()
    assert form.bool1.raw_data == None
    assert form.bool1.data == False
    assert form.bool2.data == True

    # Test with one field set to make sure behaviour is correct
    form = BoringForm(DummyPostData(bool1=[u'a']))
    assert form.bool1.raw_data == u'a'
    assert form.bool1.data == True

    # Test with model data as well.
    form = BoringForm(obj=obj)
    assert form.bool1.data == False
    assert form.bool1.raw_data == None
    assert form.bool2.data == True

    # Test with both.
    form = BoringForm(DummyPostData(bool1=[u'y']), obj=obj)
    assert form.bool1.data == True
    assert form.bool2.data == False

def test_DateTimeField():
    class F(Form):
        a = DateTimeField()
        b = DateTimeField(format='%Y-%m-%d %H:%M')
    d = datetime(2008, 5, 5, 4, 30, 0, 0)
    form = F(DummyPostData(a=['2008-05-05', '04:30:00'], b=['2008-05-05 04:30']))
    assert form.a.data == d
    assert form.a() == u"""<input id="a" name="a" type="text" value="2008-05-05 04:30:00" />"""
    assert form.b.data == d
    assert form.b() == u"""<input id="b" name="b" type="text" value="2008-05-05 04:30" />"""


def test_SubmitField():
    class F(Form):
        a = SubmitField(u'Label')
    assert F().a() == """<input id="a" name="a" type="submit" value="Label" />"""

