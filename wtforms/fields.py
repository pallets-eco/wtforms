"""
    wtforms.fields
    ~~~~~~~~~~~~~~
    
    TODO
    
    :copyright: 2007-2008 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from datetime import datetime
from cgi import escape
try:
    from functools import partial
except ImportError:
    from wtforms.utils import partial

from wtforms.validators import ValidationError

def html_params(**kwargs):
    """
    Generate HTML paramters for keywords
    """
    params = []
    for k,v in kwargs.iteritems():
        if k in ('class_', 'class__'):
            k = k[:-1]
        k = unicode(k)
        v = escape(unicode(v), quote=True)
        params.append(u'%s="%s"' % (k, v))
    return str.join(' ', params)

class Field(object):
    """
    Base field class.

    `label`
        The label of the field.
    `validators`
        A list of validators to apply to the field.
    `required`
        Whether the field is required to be entered in the form.
    `**kwargs`
        Keywords to pass to the constructor.

    This constructor is used in two different circumstances. These depend on
    whether the keys `form`, and `name` are persent in the `kwargs`:

    1. When declaring a form (`name` and `form` are not present in the
    `kwargs`, the constructor `__init__` is not actually called, but `__new__`
    creates a partial object which holds the necessary configuration to
    perform real construction.

    2. When a form is instantiated, each field is instantiated with both the
    `name` and `form` in `kwargs`, and thus the field is really instantiated,
    but with the configuration previously stored during form declaration.
    """

    _formfield = True
    creation_counter = 0
    def __new__(cls, *args, **kwargs):
        if 'name' not in kwargs:
            x = partial(cls, *args, **kwargs)
            x._formfield = True
            x.creation_counter = Field.creation_counter
            Field.creation_counter += 1
            return x
        else:
            return super(Field, cls).__new__(cls, *args, **kwargs)

    def __init__(self, label=u'', validators=[], required=True, **kwargs):
        form = kwargs['form']
        self.name = kwargs['name']
        self.id = kwargs.get('id', form._idprefix + self.name)
        self.label = Label(self.id, label)
        self.validators = validators
        self.required = required
        self.data = None
        self.errors = []

    def __unicode__(self):
        return self()

    def __call__(self, **kwargs):
        """
        Render the form field.

        `kwargs`
            html attributes to render the field with

        This method renders an HTML representation of the field. The default
        implementation raises `NotImplementedError` and so must be overriden
        in subclasses.
        """
        raise NotImplementedError

    def _get_type(self):
        return type(self).__name__
    type = property(_get_type)
        
    def _validate(self, *args):
        pass

    def process_data(self, value, has_formdata):
        """
        Process the Python data applied to this field and store the result.

        This will be called during form construction by the form's `kwargs` or
        `obj` argument.
        """
        self.data = value

    def process_formdata(self, valuelist):
        """
        Process data received over the wire from a form.

        This will be called during form cvonstruction with data supplied
        through the `formdata` argument.
        """
        self.data = valuelist[0]

class Label(object):
    """
    An HTML form label.
    """
    def __init__(self, field_id, text):
        self.field_id = field_id
        self.text = text

    def __unicode__(self):
        return self()

    def __call__(self, text=None, **kwargs):
        kwargs['for'] = self.field_id
        attributes = html_params(**kwargs)
        return u'<label %s>%s</label>' % (attributes, text or self.text)

class SelectField(Field):
    def __init__(self, label=u'', validators=[], required=True, checker=str, choices=None, *args, **kwargs):
        super(SelectField, self).__init__(label, validators, required, *args, **kwargs)
        self.checker = checker
        self.choices = choices

    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        html = u'<select %s>' % html_params(name=self.name, **kwargs)
        for val,title in self.choices:
            options = {'value': val}
            if self._selected(val):
                options['selected'] = u'selected'
            html += u'<option %s>%s</option>' % (html_params(**options), escape(unicode(title)))
        html += u'</select>'
        return html

    def _selected(self, value):
        return (self.checker(value) == self.data)

    def process_data(self, value, has_formdata):
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
        return super(SelectMultipleField, self).__call__(multiple="multiple", **kwargs)

    def _selected(self, value):
        if self.data is not None:
            return (self.checker(value) in self.data)
        
    def process_formdata(self, valuelist):
        self.data = [self.checker(x) for x in valuelist]

    def _validate(self, *args):
        choices = [c[0] for c in self.choices]
        for d in self.data:
            if d not in choices:
                raise ValidationError(u"'%s' is not a valid choice for this field" % d)
        
        
class TextField(Field):
    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        kwargs.setdefault('type', 'text')
        return u'<input %s />' % html_params(name=self.name, value=self._value(), **kwargs) 

    def _value(self):
        return self.data and unicode(self.data) or u''

class HiddenField(TextField):
    def __call__(self, **kwargs):
        kwargs.setdefault('type', 'hidden')
        return super(HiddenField, self).__call__(**kwargs)

class TextAreaField(TextField):
    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        return u'<textarea %s>%s</textarea>' % (html_params(name=self.name, **kwargs), escape(unicode(self._value())))

class PasswordField(TextField):
    def __call__(self, **kwargs):
        kwargs.setdefault('type', 'password')
        return super(PasswordField, self).__call__(**kwargs)
        
class FileField(TextField):
    """
    Can render a file-upload field.  Will take any passed filename value, if
    any is sent by the browser in the post params.  This field will NOT 
    actually handle the file upload portion, as wtforms does not deal with 
    individual frameworks' file handling capabilities.
    """
    def __call__(self, **kwargs):
        kwargs.setdefault('type', 'file')
        return super(FileField, self).__call__(**kwargs)

class IntegerField(TextField):
    """ Can be represented by a text-input """

    def _value(self):
        return self.data and unicode(self.data) or u'0'

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
    
    def process_data(self, value, has_formdata):
        if has_formdata:
            self.data = False
        else:
            self.data = value

    def process_formdata(self, valuelist):
        self.data = valuelist[0] == u'y'

class DateTimeField(TextField):
    """ Can be represented by one or multiple text-inputs """
    def __init__(self, label=u'', validators=[], required=True, *args, **kwargs):
        super(DateTimeField, self).__init__(label, validators, required, *args, **kwargs)
        self.format = kwargs.pop('format', '%Y-%m-%d %H:%M:%S')

    def _value(self):
        return self.data and self.data.strftime(self.format) or u''

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            try:
                self.data = datetime.strptime(str.join(' ', valuelist), self.format)
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

__all__ = ('SelectField', 'SelectMultipleField', 'TextField', 'IntegerField', 'BooleanField', 'DateTimeField', 'PasswordField', 'TextAreaField', 'SubmitField', 'HiddenField', 'FileField')
