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

from wtforms.utils import html_params
from wtforms.validators import ValidationError

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
        if '_name' not in kwargs:
            x = partial(cls, *args, **kwargs)
            x._formfield = True
            x.creation_counter = Field.creation_counter
            Field.creation_counter += 1
            return x
        else:
            return super(Field, cls).__new__(cls, *args, **kwargs)

    def __init__(self, label=u'', validators=None, description=u'', id=None, default=None, _form=None, _name=None):
        form = _form
        self.name = _name
        self.id = id or (form._idprefix + self.name)
        self.label = Label(self.id, label)
        if validators is None:
            validators = []
        self.validators = validators
        self.description = description
        self.type = type(self).__name__
        self._default = default
        self.errors = []

    def __unicode__(self):
        return self()

    def __str__(self):
        return self()

    def __call__(self, **kwargs):
        """
        Render this field as HTML, using keyword args as additional attributes.

        Any HTML attribute passed to the method will be added to the tag
        and entity-escaped properly.   
        """
        raise NotImplementedError

    def validate(self, *args):
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

    def __str__(self):
        return self()

    def __unicode__(self):
        return self()

    def __call__(self, text=None, **kwargs):
        kwargs['for'] = self.field_id
        attributes = html_params(**kwargs)
        return u'<label %s>%s</label>' % (attributes, text or self.text)

class SelectField(Field):
    def __init__(self, label=u'', validators=None, checker=unicode, choices=None, **kwargs):
        super(SelectField, self).__init__(label, validators, **kwargs)
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
        try:
            self.data = self.checker(getattr(value, 'id', value))
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        self.data = self.checker(valuelist[0])

    def validate(self, *args):
        for v, _ in self.choices:
            if self.data == v:
                break
        else:
            raise ValidationError('Not a valid choice')

class SelectMultipleField(SelectField):
    """
    No different from a normal select field, except this one can take (and
    validate) multiple choices.  You'll need to specify the HTML `rows`
    attribute to the select field when rendering.
    """

    def __call__(self, **kwargs):
        return super(SelectMultipleField, self).__call__(multiple="multiple", **kwargs)

    def _selected(self, value):
        if self.data is not None:
            return (self.checker(value) in self.data)
        
    def process_formdata(self, valuelist):
        self.data = [self.checker(x) for x in valuelist]

    def validate(self, *args):
        choices = [c[0] for c in self.choices]
        for d in self.data:
            if d not in choices:
                raise ValidationError(u"'%s' is not a valid choice for this field" % d)
        
        
class TextField(Field):
    """
    This field is the base for most of the more complicated fields, and
    represents an ``<input type="text">``.  
    """

    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        kwargs.setdefault('type', 'text')
        return u'<input %s />' % html_params(name=self.name, value=self._value(), **kwargs) 

    def _value(self):
        return self.data and unicode(self.data) or u''

class HiddenField(TextField):
    """
    Represents an ``<input type="hidden">``.
    """

    def __call__(self, **kwargs):
        kwargs.setdefault('type', 'hidden')
        return super(HiddenField, self).__call__(**kwargs)

class TextAreaField(TextField):
    """
    This field represents an HTML ``<textarea>`` and can be used to take multi-line input.
    """

    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        return u'<textarea %s>%s</textarea>' % (html_params(name=self.name, **kwargs), escape(unicode(self._value())))

class PasswordField(TextField):
    """
    Represents an ``<input type="password">``.
    """

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
    """
    A text field, except all input is coerced to an integer.  Erroneous input
    is ignored and will not be accepted as a value.
    """

    def _value(self):
        return self.data and unicode(self.data) or u'0'

    def process_formdata(self, valuelist):
        try:
            self.data = int(valuelist[0])
        except ValueError:
            pass

class BooleanField(Field):
    """ 
    Represents an ``<input type="checkbox">``.
    """

    def __init__(self, label=u'', validators=None, **kwargs):
        super(BooleanField, self).__init__(label, validators, **kwargs)
        self.raw_data = None

    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        kwargs.setdefault('type', 'checkbox')
        kwargs.setdefault('value', 'y')
        if self.data:
            kwargs['checked'] = u'checked'
        return u'<input %s />' % html_params(name=self.name, **kwargs)
    
    def process_data(self, value, has_formdata):
        if has_formdata:
            self.data = False
        else:
            self.raw_data = value
            self.data = bool(value)

    def process_formdata(self, valuelist):
        if valuelist:
            self.raw_data = valuelist[0]
            self.data = bool(valuelist[0])

class DateTimeField(TextField):
    """ Can be represented by one or multiple text-inputs """

    def __init__(self, label=u'', validators=None, format='%Y-%m-%d %H:%M:%S', **kwargs):
        super(DateTimeField, self).__init__(label, validators, **kwargs)
        self.format = format

    def _value(self):
        return self.data and self.data.strftime(self.format) or u''

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            try:
                self.data = datetime.strptime(str.join(' ', valuelist), self.format)
            except ValueError:
                pass

class SubmitField(BooleanField):
    """
    Represents an ``<input type="submit">``.  This allows checking if a given
    submit button has been pressed.
    """

    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        kwargs.setdefault('type', 'submit')
        kwargs.setdefault('value', self.label.text)
        return u'<input %s />' % html_params(name=self.name, **kwargs) 

__all__ = (
    'BooleanField', 'DateTimeField', 'FileField', 'HiddenField',
    'IntegerField', 'PasswordField', 'SelectField', 'SelectMultipleField',
    'SubmitField', 'TextField', 'TextAreaField',
)
