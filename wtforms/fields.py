from cgi import escape
from datetime import datetime
from decimal import Decimal, InvalidOperation
from itertools import chain, count
import time

from wtforms import widgets
from wtforms.validators import StopValidation, ValidationError

__all__ = (
    'BooleanField', 'DecimalField', 'DateTimeField', 'FieldList', 'FileField', 'FormField',
    'HiddenField', 'IntegerField', 'PasswordField', 'RadioField',
    'SelectField', 'SelectMultipleField', 'SubmitField', 'TextField',
    'TextAreaField',
)

_unset_value = object()

class Field(object):
    """
    Field base class
    """
    widget = None
    errors = tuple()
    _formfield = True

    def __new__(cls, *args, **kwargs):
        if '_form' in kwargs and '_name' in kwargs:
            return super(Field, cls).__new__(cls)
        else:
            return UnboundField(cls, *args, **kwargs)

    def __init__(self, label=u'', validators=None, filters=tuple(), description=u'', id=None, default=None, widget=None, _form=None, _name=None):
        """
        Construct a new field.

        :param label:
            The label of the field. Available after construction through the
            `label` property.
        :param description:
            A description for the field, typically used for help text. It is
            available through the `description` property after construction.
        :param id:
            An id to use for the field. A reasonable default is set by the form,
            and you shouldn't need to set this manually.
        :param validators:
            A sequence of validators to call when `validate` is called.
        :param filters:
            A sequence of filters which are run on input data by `process`.
        :param default:
            The default value to assign to the field, if one is not provided by
            the form.
        :param widget:
            If provided, overrides the widget used to render the field.
        :param _form:
            The form holding this field. It is passed by the form itself during
            construction. You should never pass this value yourself.
        :param _name:
            The name of this field, passed by the enclosing form during its
            construction. You should never pass this value yourself.

        If `_form` and `_name` isn't provided, an :class:`UnboundField` will be
        returned instead. Call its :func:`bind` method with a form instance and
        a name to construct the field.
        """
        self.name = _name
        self.id = id or (_form._idprefix + self.name)
        self.label = Label(self.id, label)
        if validators is None:
            validators = []
        self.validators = validators
        self.filters = filters
        self.description = description
        self.type = type(self).__name__
        self.flags = Flags()
        try:
            self._default = default()
        except TypeError:
            self._default = default
        for v in validators:    
            flags = getattr(v, 'field_flags', ())
            for f in flags:
                setattr(self.flags, f, True)
        if widget:
            self.widget = widget

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
        return self.widget(self, **kwargs)

    def validate(self, form, extra_validators=tuple()):
        """
        Validates the field and returns True or False. `self.errors` will
        contain any errors raised during validation. This is usually only
        called by `Form.validate`.
        
        Subfields shouldn't override this, but rather override either
        `pre_validate`, `post_validate` or both, depending on needs.
        
        :param form: The form the field belongs to.
        :param extra_validators: A list of extra validators to run.
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
        
        :param form: The form the field belongs to.
        """
        pass
        
    def post_validate(self, form, validation_stopped):
        """
        Override if you need to run any field-level validation tasks after
        normal validation. This shouldn't be needed in most cases.
        
        :param form: The form the field belongs to.
        :param validation_stopped:
            `True` if any validator raised StopValidation.
        """
        pass

    def process(self, formdata, data=_unset_value): 
        """
        Process incoming data, calling process_data, process_formdata as needed, and run filters.

        If `data` is not provided, process_data will be called on the field's default.

        Field subclasses usually won't override this, instead overriding the
        process_formdata and process_data methods. Only override this for
        special advanced processing, such as when a field encapsulates many inputs.
        """
        if data is _unset_value:
            self.process_data(self._default)
        else:
            self.process_data(data)

        if formdata is not None:
            if self.name in formdata:
                try:
                    self.process_formdata(formdata.getlist(self.name))
                except AttributeError:
                    self.process_formdata(formdata.getall(self.name))
            else:
                self.process_formdata([])

        for filter in self.filters:
            self.data = filter(self.data)
                
    def process_data(self, value):
        """
        Process the Python data applied to this field and store the result.

        This will be called during form construction by the form's `kwargs` or
        `obj` argument.
        
        :param value: The python object containing the value to process.
        """
        self.data = value

    def process_formdata(self, valuelist):
        """
        Process data received over the wire from a form.

        This will be called during form construction with data supplied
        through the `formdata` argument.
        
        :param valuelist: A list of strings to process.
        """
        if valuelist:
            self.data = valuelist[0]

    def populate(self, obj, name):
        """
        Populates `obj.<name>` with the field's data.

        :note: 
            This is a destructive operation. If `obj.<name>` already exists, it
            will be overridden. Use with caution.
        """
        setattr(obj, name, self.data)

class UnboundField(object):
    _formfield = True
    creation_counter = 0

    def __init__(self, field_class, *args, **kwargs):
        UnboundField.creation_counter += 1
        self.field_class = field_class
        self.args = args
        self.kwargs = kwargs
        self.creation_counter = UnboundField.creation_counter

    def bind(self, form, name, **kwargs):
        return self.field_class(_form=form, _name=name, *self.args, **dict(self.kwargs, **kwargs))

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
        attributes = widgets.html_params(**kwargs)
        return u'<label %s>%s</label>' % (attributes, text or self.text)

class SelectField(Field):
    widget = widgets.Select()

    def __init__(self, label=u'', validators=None, coerce=unicode, choices=None, **kwargs):
        super(SelectField, self).__init__(label, validators, **kwargs)
        self.coerce = coerce
        self.choices = choices

    def iter_choices(self):
        for value, label in self.choices:
            yield (value, label, self.coerce(value) == self.data)

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
    widget = widgets.Select(multiple=True)

    def iter_choices(self):
        for value, label in self.choices:
            selected = self.data is not None and self.coerce(value) in self.data
            yield (value, label, selected)

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
    widget = widgets.ListWidget(prefix_label=False)

    def __iter__(self):
        for i, (value, label, checked) in enumerate(self.iter_choices()):
            r = self._Radio(label=label, id=u'%s_%d' % (self.id, i), _name=self.name, _form=None)
            r.process_data(value)
            r.checked = checked
            yield r

    class _Radio(Field):
        widget = widgets.RadioInput()
        checked = False
        
class TextField(Field):
    """
    This field is the base for most of the more complicated fields, and
    represents an ``<input type="text">``.  
    """
    widget = widgets.TextInput()

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]
        else:
            self.data = u''

    def _value(self):
        return self.data is not None and unicode(self.data) or u''

class HiddenField(TextField):
    """
    Represents an ``<input type="hidden">``.
    """
    widget = widgets.HiddenInput()

class TextAreaField(TextField):
    """
    This field represents an HTML ``<textarea>`` and can be used to take
    multi-line input.
    """
    widget = widgets.TextArea()

class PasswordField(TextField):
    """
    Represents an ``<input type="password">``.
    """
    widget = widgets.PasswordInput()
        
class FileField(TextField):
    """
    Can render a file-upload field.  Will take any passed filename value, if
    any is sent by the browser in the post params.  This field will NOT 
    actually handle the file upload portion, as wtforms does not deal with 
    individual frameworks' file handling capabilities.
    """
    widget = widgets.FileInput()

class IntegerField(TextField):
    """
    A text field, except all input is coerced to an integer.  Erroneous input
    is ignored and will not be accepted as a value.
    """
    def __init__(self, label=u'', validators=None, **kwargs):
        super(IntegerField, self).__init__(label, validators, **kwargs)
        self.raw_data = None

    def _value(self):
        if self.raw_data is not None:
            return self.raw_data
        else:
            return self.data and unicode(self.data) or u'0'

    def process_formdata(self, valuelist):
        if valuelist:
            self.raw_data = valuelist[0]
            try:
                self.data = int(valuelist[0])
            except ValueError:
                pass

    def post_validate(self, form, validation_stopped):
        if not validation_stopped and self.raw_data:
            try:
                int(self.raw_data)
            except ValueError:
                raise ValidationError(u'Not a valid integer value')

class DecimalField(TextField):
    """
    A text field which displays and coerces data of the `decimal.Decimal` type.

    Defining the `number_format` parameter to the constructor allows you to
    customize how the number is displayed, using standard python string
    formatting rules.
    """
    
    def __init__(self, label=u'', validators=None, number_format='%0.2f', **kwargs):
        super(DecimalField, self).__init__(label, validators, **kwargs)
        self.raw_data = None
        self.number_format = number_format

    def _value(self):
        if self.data is not None:
            return self.number_format % self.data
        elif self.raw_data is not None:
            return self.raw_data
        else:
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.raw_data = valuelist[0]
            try:
                self.data = Decimal(valuelist[0])
            except (InvalidOperation, ValueError):
                pass


class BooleanField(Field):
    """ 
    Represents an ``<input type="checkbox">``.
    """
    widget = widgets.CheckboxInput()

    def __init__(self, label=u'', validators=None, **kwargs):
        super(BooleanField, self).__init__(label, validators, **kwargs)
        self.raw_data = None

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
        self.raw_data = None

    def _value(self):
        if self.raw_data is not None:
            return self.raw_data
        else:
            return self.data and self.data.strftime(self.format) or u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.raw_data = str.join(' ', valuelist)
            try:
                timetuple = time.strptime(self.raw_data, self.format)
                self.data = datetime(*timetuple[:7])
            except ValueError:
                self.data = None

class SubmitField(BooleanField):
    """
    Represents an ``<input type="submit">``.  This allows checking if a given
    submit button has been pressed.
    """
    widget = widgets.SubmitInput()

class FormField(Field):
    """
    Encapsulate a form as a field in another form.
    
    The required `form_class` argument to the constructor should be a subclass
    of `Form`.
    """
    widget = widgets.TableWidget()

    def __init__(self, form_class, label=u'', validators=None, **kwargs):
        super(FormField, self).__init__(label, validators, **kwargs)
        self.form_class = form_class
        if self.filters:
            raise TypeError('FormField cannot take filters, as the encapsulated data is not mutable.')
        if validators:
            raise TypeError('FormField does not accept any validators. Instead, define them on the enclosed form.')

        if '_form' in kwargs and kwargs['_form']:
            self._idprefix = kwargs['_form']._idprefix
        else:
            self._idprefix = ''
        self._hidden_field = HiddenField(id=self.id + '-_marker', default='__FormField', _form=None, _name=self.name)
        self._hidden_field.process(None)
    
    def process(self, formdata, data=_unset_value):
        if data is _unset_value:
            data = None

        if isinstance(data, dict):
            self.form = self.form_class(formdata=formdata, prefix=self.name, idprefix=self._idprefix, **data)
        else:
            self.form = self.form_class(formdata=formdata, obj=data, prefix=self.name, idprefix=self._idprefix)            

    def validate(self, form, extra_validators=tuple()):
        if extra_validators:
            raise TypeError('FormField does not accept in-line validators, as it gets errors from the enclosed form.')
        return self.form.validate()

    def populate(self, obj, name):
        self.form.auto_populate(getattr(obj, name))

    def __iter__(self):
        yield self._hidden_field
        for field in self.form:
            yield field

    def _get_data(self):
        return self.form.data
    data = property(_get_data)

    def _get_errors(self):
        return self.form.errors
    errors = property(_get_errors)

class FieldList(Field):
    """
    Encapsulate an ordered list of multiple instances of the same field type,
    keeping data as a list.

    >>> authors = FieldList(TextField('Name', [validators.required()]), 
    ...                     blank_entries=1)

    :param unbound_field:
        A partially-instantiated field definition, just like that would be
        defined on a form directly.
    :param blank_entries:
        If set to a non-zero value, will add a number of blank subfields to the
        list with no data; useful for sub-record edit forms.
    """
    widget=widgets.ListWidget()

    def __init__(self, unbound_field, label=u'', validators=None, blank_entries=0, **kwargs):
        super(FieldList, self).__init__(label, validators, **kwargs)
        assert isinstance(unbound_field, UnboundField), 'Field must be unbound, not a field class'
        self.unbound_field = unbound_field
        self.blank_entries = blank_entries

    def process(self, formdata, data=_unset_value):
        if data is _unset_value or not data:
            data = ()
        self.fields = []
        for i in count():
            name = '%s-%d' % (self.name, i)
            try:
                obj_data = data[i]
            except IndexError:
                if not formdata or name not in formdata:
                    break # If there's no data or formdata, we're done
                obj_data = _unset_value
            f = self.add_entry(False)
            f.process(formdata, obj_data)
        if not formdata and self.blank_entries:
            for _ in xrange(self.blank_entries):
                self.add_entry()

    def validate(self, form, extra_validators=tuple()):
        self.errors = []
        success = True
        for subfield in self.fields:
            if not subfield.validate(form):
                success = False
                self.errors.extend(subfield.errors)
        return success

    def add_entry(self, process=True):
        new_index = len(self.fields)
        name = '%s-%d' % (self.name, new_index)
        id   = '%s-%d' % (self.id, new_index)
        f = self.unbound_field.bind(form=None, name=name, id=id)
        if process:
            f.process(None)
        self.fields.append(f)
        return f

    def __iter__(self):
        return iter(self.fields)

    def _get_data(self):
        return [f.data for f in self.fields]
    data = property(_get_data)

