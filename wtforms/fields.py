"""
    wtforms.fields
    ~~~~~~~~~~~~~~
    
    TODO
    
    :copyright: 2007 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from datetime import datetime
from cgi import escape
from functools import partial

from .validators import ValidationError

def html_params(**params):
    return str.join(' ', (u'%s="%s"' % (unicode(k), escape(unicode(v), quote=True)) for k,v in params.iteritems()))

class Field(object):
    _formfield = True
    def __new__(cls, *args, **kwargs):
        if 'name' not in kwargs:
            x = partial(cls, *args, **kwargs)
            x._formfield = True
            return x
        else:
            return super(Field, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.jinja_allowed_attributes = None # Ugly hack to let jinja access our attributes
        form = kwargs['form']
        self.name = kwargs['name']
        self.id = kwargs.get('id', form.idprefix + self.name)
        self._label = args[0]
        self.validators = args[1:]
        self.data = None
        self.errors = []

    def __unicode__(self):
        return self()

    def __call__(self, **kwargs):
        raise NotImplementedError

    def _get_label(self):
        return '<label for="%s">%s</label>' % (self.id, self._label)
    label = property(_get_label)
        
    def _validate(self, *args):
        pass

    def process_formdata(self, valuelist):
        self.data = valuelist[0]

    def process_modeldata(self, value, in_form):
        self.data = value

class SelectField(Field):
    checker = str

    def __init__(self, *args, **kwargs):
        super(SelectField, self).__init__(*args, **kwargs)
        if 'checker' in kwargs:
            self.checker = kwargs['checker']
        self.choices = kwargs.pop('choices', None)

    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        html = u'<select %s>' % html_params(name=self.name, **kwargs)
        for val,title in self.choices:
            html += u'<option value="%s"%s>%s</option>' % (escape(unicode(val), quote=True), (u' selected="selected"' if self._selected(val) else ''), escape(unicode(title)))
        html += u'</select>'
        return html

    def _selected(self, value):
        return (self.checker(value) == self.data)

    def process_modeldata(self, value, in_form):
        self.data = self.checker(getattr(value, 'id', value))

    def process_formdata(self, valuelist):
        self.data = self.checker(valuelist[0])

    def _validate(self, *args):
        for v, _ in self.choices:
            if self.data == v:
                break
        else:
            raise ValidationError('Not a valid choice')

class SelectMultipleField(SelectField):
    def __call__(self, **kwargs):
        super(SelectMultipleField, self).__call__(multiple="multiple", **kwargs)

    def _selected(self, value):
        return (self.checker(value) in self.data)
        
    def process_formdata(self, valuelist):
        self.data = list(self.checker(x) for x in valuelist)
        
class TextField(Field):
    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        kwargs.setdefault('type', 'text')
        return u'<input %s />' % html_params(name=self.name, value=self._value(), **kwargs) 

    def _value(self):
        return unicode(self.data) if self.data else u''

class TextAreaField(TextField):
    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        return u'<textarea %s>%s</textarea>' % (html_params(name=self.name, **kwargs), escape(unicode(self._value())))

class PasswordField(TextField):
    def __call__(self, **kwargs):
        kwargs.setdefault('type', 'password')
        return super(PasswordField, self).__call__(**kwargs)
        
class IntegerField(TextField):
    """ Can be represented by a text-input """

    def _value(self):
        return unicode(self.data) if self.data else u'0'

    def process_formdata(self, valuelist):
        try:
            self.data = int(valuelist[0])
        except ValueError:
            pass

class BooleanField(Field):
    """ Represents a checkbox."""

    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        kwargs.setdefault('type', 'checkbox')
        if self.data:
            kwargs['checked'] = u'checked'
        return u'<input %s />' % html_params(name=self.name, value=u'y', **kwargs)
    
    def process_formdata(self, valuelist):
        self.data = valuelist[0] == u'y'

    def process_modeldata(self, value, in_form):
        self.data = False if in_form else value

class DateTimeField(TextField):
    """ Can be represented by one or multiple text-inputs """
    def __init__(self, *args, **kwargs):
        super(DateTimeField, self).__init__(*args, **kwargs)
        self.format = kwargs.pop('format', '%Y-%m-%d %H:%M:%S')

    def _value(self):
        return self.data.strftime(self.format) if self.data else u''

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            try:
                self.data = datetime.strptime(str.join(" ", valuelist), self.format)
            except ValueError:
                return u'Date is invalid.'

class SubmitField(BooleanField):
    """Allow checking if a given submit button has been pressed"""
    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        kwargs.setdefault('type', 'submit')
        kwargs.setdefault('value', self._label)
        return u'<input %s />' % html_params(name=self.name, **kwargs) 

    def process_formdata(self, valuelist):
        self.data = (len(valuelist) > 0 and valuelist[0] != u'')

__all__ = ('SelectField', 'SelectMultipleField', 'TextField', 'IntegerField', 'BooleanField', 'DateTimeField', 'PasswordField', 'TextAreaField', 'SubmitField')
