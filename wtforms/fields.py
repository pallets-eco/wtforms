"""
    wtforms.fields
    ~~~~~~~~~~~~~~
    
    Contains the `Field` base class in addition to all built-in field types.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from datetime import datetime
from cgi import escape
from itertools import chain
import time

from wtforms.utils import html_params
from wtforms.validators import ValidationError, StopValidation

class Field(object):
    """
    Stores and processes data, and generates HTML for an form field.

    Field instances contain the data of that instance as well as the
    functionality to render it within your Form. They also contain a number of
    properties which can be used within your templates to render the field and
    label.  
    """
    _formfield = True

    def __new__(cls, *args, **kwargs):
        if '_form' in kwargs and '_name' in kwargs:
            return super(Field, cls).__new__(cls)
        else:
            return UnboundField(cls, *args, **kwargs)

    def __init__(self, label=u'', validators=None, description=u'', id=None, default=None, _form=None, _name=None):
        self.name = _name
        self.id = id or (_form._idprefix + self.name)
        self.label = Label(self.id, label)
        if validators is None:
            validators = []
        self.validators = validators
        self.description = description
        self.type = type(self).__name__
        self._default = default
        self.flags = Flags()
        for v in validators:    
            flags = getattr(v, 'field_flags', ())
            for f in flags:
                setattr(self.flags, f, True)
        self.errors = []

    def __unicode__(self):
        """
        Returns a HTML representation of the field. For more powerful rendering,
        see the `__call__` method.
        """
        return self()

    def __str__(self):
        """
        Returns a HTML representation of the field. For more powerful rendering,
        see the `__call__` method.
        """
        return self()

    def __call__(self, **kwargs):
        """
        Render this field as HTML, using keyword args as additional attributes.

        Any HTML attribute passed to the method will be added to the tag
        and entity-escaped properly.   
        """
        raise NotImplementedError

    def validate(self, form, extra_validators=tuple()):
        """
        Validates the field and returns True or False. `self.errors` will
        contain any errors raised during validation. This is usually only
        called by `Form.validate`.
        
        Subfields shouldn't override this, but rather override either
        `pre_validate`, `post_validate` or both, depending on needs.
        
        `form`
            The form the field belongs to.
        `extra_validators`
            A list of extra validators to run.
        """
        self.errors = []
        stop_validation = False

        # Call pre_validate
        try:
            self.pre_validate(form)
        except StopValidation, e:
            if e.args and e.args[0]:
                self.errors.append(e.args[0])
            stop_validation = True
        except ValueError, e:
            self.errors.append(e.args[0])

        # Run validators
        if not stop_validation:
            for validator in chain(self.validators, extra_validators):
                try:
                    validator(form, self)
                except StopValidation, e:
                    if e.args and e.args[0]:
                        self.errors.append(e.args[0])
                    stop_validation = True
                    break
                except ValueError, e:
                    self.errors.append(e.args[0])
        
        # Call post_validate
        try:
            self.post_validate(form, stop_validation)
        except ValueError, e:
            self.errors.append(e.args[0])

        return len(self.errors) == 0

    def pre_validate(self, form):
        """
        Override if you need field-level validation. Runs before any other
        validators.
        
        `form`
            The form the field belongs to.
        """
        pass
        
    def post_validate(self, form, validation_stopped):
        """
        Override if you need to run any field-level validation tasks after
        normal validation. This shouldn't be needed in most cases.
        
        `form`
            The form the field belongs to.
        `validation_stopped`
            `True` if any validator raised StopValidation.
        """
        pass

    def process_data(self, value):
        """
        Process the Python data applied to this field and store the result.

        This will be called during form construction by the form's `kwargs` or
        `obj` argument.
        
        `value`
            The python object containing the value to process.
        """
        self.data = value

    def process_formdata(self, valuelist):
        """
        Process data received over the wire from a form.

        This will be called during form construction with data supplied
        through the `formdata` argument.
        
        `valuelist`
            A list of strings to process.
        """
        if valuelist:
            self.data = valuelist[0]

class UnboundField(object):
    _formfield = True
    creation_counter = 0

    def __init__(self, field_class, *args, **kwargs):
        UnboundField.creation_counter += 1
        self.field_class = field_class
        self.args = args
        self.kwargs = kwargs
        self.creation_counter = UnboundField.creation_counter
        self.name = None

    def bind(self, form, name):
        return self.field_class(_form=form, _name=name, *self.args, **self.kwargs)

    def __cmp__(self, x):
        return cmp(self.creation_counter, x.creation_counter)

    def __repr__(self):
        return '<UnboundField(%s, %r, %r)>' % (self.field_class.__name__, self.args, self.kwargs)

class Flags(object):
    """
    Holds a set of boolean flags as attributes.

    Accessing a non-existing attribute returns False for its value.
    """
    def __getattr__(self, name):
        return False

    def __contains__(self, name):
        return getattr(self, name)


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
    def __init__(self, label=u'', validators=None, coerce=unicode, choices=None, **kwargs):
        super(SelectField, self).__init__(label, validators, **kwargs)
        self.coerce = coerce
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
        return (self.coerce(value) == self.data)

    def process_data(self, value):
        try:
            self.data = self.coerce(getattr(value, 'id', value))
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = self.coerce(valuelist[0])
            except ValueError:
                pass

    def pre_validate(self, form):
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
            return (self.coerce(value) in self.data)
        
    def process_data(self, value):
        try:
            self.data = [self.coerce(getattr(v, 'id', v)) for v in value]
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        try:
            self.data = [self.coerce(x) for x in valuelist]
        except ValueError:
            pass

    def pre_validate(self, form):
        choices = [c[0] for c in self.choices]
        for d in self.data:
            if d not in choices:
                raise ValidationError(u"'%s' is not a valid choice for this field" % d)

class RadioField(SelectField):
    """
    Like a SelectField, except displays a list of radio buttons.

    Iterating the field will produce  subfields (each containing a label as 
    well) in order to allow custom rendering of the individual radio fields.
    """
    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        html = u'<ul %s>' % html_params(**kwargs)
        for choice in self:
            html += u'<li>%s %s</li>' % (choice, choice.label)
        html += u'</ul>'
        return html

    def __iter__(self):
        for i, (value, label) in enumerate(self.choices):
            r = self._Radio(label=label, id=u'%s_%d' % (self.id, i), _name=self.name, _form=None)
            r.process_data(value)
            r.checked = self._selected(value)
            yield r

    class _Radio(Field):
        checked = False
        def __call__(self, **kwargs):
            kwargs.setdefault('id', self.id)
            kwargs.setdefault('type', 'radio')
            if self.checked:
                kwargs['checked'] = u'checked'
            kwargs['name'] = self.name
            kwargs['value'] = self.data
            return u'<input %s />' % html_params(**kwargs)
        
        
class TextField(Field):
    """
    This field is the base for most of the more complicated fields, and
    represents an ``<input type="text">``.  
    """
    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        kwargs.setdefault('type', 'text')
        return u'<input %s />' % html_params(name=self.name, value=self._value(), **kwargs) 

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]
        else:
            self.data = u''

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
        kwargs.setdefault('type', u'checkbox')
        kwargs.setdefault('value', u'y')
        if self.data:
            kwargs['checked'] = u'checked'
        return u'<input %s />' % html_params(name=self.name, **kwargs)
    
    def process_data(self, value):
        self.raw_data = value
        self.data = bool(value)

    def process_formdata(self, valuelist):
        if valuelist:
            self.raw_data = valuelist[0]
            self.data = bool(valuelist[0])
        else:
            self.raw_data = None
            self.data = False

class DateTimeField(TextField):
    """
    Can be represented by one or multiple text-inputs.
    """
    def __init__(self, label=u'', validators=None, format='%Y-%m-%d %H:%M:%S', **kwargs):
        super(DateTimeField, self).__init__(label, validators, **kwargs)
        self.format = format

    def _value(self):
        return self.data and self.data.strftime(self.format) or u''

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            try:
                timetuple = time.strptime(str.join(' ', valuelist), self.format)
		self.data = datetime(*timetuple[:7])
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
    'IntegerField', 'PasswordField', 'RadioField', 'SelectField', 'SelectMultipleField',
    'SubmitField', 'TextField', 'TextAreaField',
)
