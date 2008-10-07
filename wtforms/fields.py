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
    Stores and processes data, and generates HTML for an form field.

    Field instances contain the data of that instance as well as the
    functionality to render it within your Form. They also contain a number of
    properties which can be used within your templates to render the field and
    label.  
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

    def __init__(self, label=u'', validators=None, required=True, description=u'', id=None, **kwargs):
        form = kwargs['form']
        self.name = kwargs['name']
        self.id = id or (form._idprefix + self.name)
        self.label = Label(self.id, label)
        if validators is None:
            validators = []
        self.validators = validators
        self.required = required
        self.description = description
        self.type = type(self).__name__
        self.data = None
        self.errors = []

    def __unicode__(self):
        return self()

    def __call__(self, **kwargs):
        """
        Render this field as HTML, using keyword args as additional attributes.

        Any HTML attribute passed to the constructor will be added to the tag
        and entity-escaped properly.   
        """
        raise NotImplementedError

    def _validate(self, *args):
        """
        Run any built-in implicit validation provided by this field.

        Most fields don't need to implement this, but any field can if needed.
        """
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
    def __init__(self, label=u'', validators=[], required=True, checker=unicode, choices=None, *args, **kwargs):
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
        kwargs.setdefault('value', self.label.text)
        return u'<input %s />' % html_params(name=self.name, **kwargs) 

    def process_formdata(self, valuelist):
        self.data = (len(valuelist) > 0 and valuelist[0] != u'')

__all__ = ('SelectField', 'SelectMultipleField', 'TextField', 'IntegerField', 'BooleanField', 'DateTimeField', 'PasswordField', 'TextAreaField', 'SubmitField', 'HiddenField', 'FileField')
