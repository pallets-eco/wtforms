"""
    wtforms.form
    ~~~~~~~~~~~~
    
    The `Form` base class.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from wtforms.validators import StopValidation

class FormMeta(type):
    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)
        cls._unbound_fields = None
        for name, v in attrs.iteritems():
            if hasattr(v, '_formfield'):
                v.name = name

    def __call__(cls, *args, **kwargs):
        if cls._unbound_fields is None:
            fields = []
            for name in dir(cls):
                if not name.startswith('_'):
                    unbound_field = getattr(cls, name)
                    if  hasattr(unbound_field, '_formfield'):
                        fields.append(unbound_field)
            fields.sort()
            cls._unbound_fields = fields
        return type.__call__(cls, *args, **kwargs)

    def __setattr__(cls, name, value):
        if not name.startswith('_') and hasattr(value, '_formfield'):
            value.name = name
            cls._unbound_fields = None
        type.__setattr__(cls, name, value)

    def __delattr__(cls, name):
        if not name.startswith('_'):
            cls._unbound_fields = None
        type.__delattr__(cls, name)

class Form(object):
    __metaclass__ = FormMeta
    def __init__(self, formdata=None, obj=None, prefix='', idprefix='', **kwargs):
        if prefix:
            prefix += '_'
        self._idprefix = idprefix

        # populate data from form and optional instance and defaults
        self._errors = None
        self._fields = []
        has_formdata = bool(formdata)
        for u_field in self._unbound_fields:
            name = u_field.name
            form_name = prefix + name
            field = u_field.bind(_form=self, _name=form_name)
            self._fields.append((name, field))
            setattr(self, name, field)

            if hasattr(obj, name):
                field.process_data(getattr(obj, name))
            elif name in kwargs:
                field.process_data(kwargs[name])
            else:
                field.process_data(field._default)

            if has_formdata:
                if form_name in formdata:
                    try:
                        data = formdata.getlist(form_name)
                    except AttributeError:
                        data = formdata.getall(form_name)
                    field.process_formdata(data)
                else:
                    field.process_formdata([])

    def __iter__(self): 
        """
        Iterate form fields in their order of definition on the form.
        """
        for name, field in self._fields:
            yield field

    def __contains__(self, item):
        """      
        Returns `True` if the named field is a member of this form.
        """
        return getattr(getattr(self, item, False), '_formfield', False) is True

    def __delattr__(self, name): 
        try: 
            self._fields.remove((name, getattr(self, name)))
            setattr(self, name, None)
        except ValueError:
            super(Form, self).__delattr__(name)

    def validate(self):
        """
        Validates the form by calling `validate` on each field, passing any
        extra `Form.validate_<fieldname>` validators to the field validator.
        
        Returns `True` if no errors occur.
        """
        self._errors = None
        success = True
        for name, field in self._fields:
            extra = []
            inline = getattr(self.__class__, 'validate_%s' % name, None)
            if inline is not None:
                extra.append(inline)
            if not field.validate(self, extra):
                success = False
        return success

    def _get_data(self):
        data = {}
        for name, field in self._fields:
            data[name] = field.data
        return data
    data = property(_get_data)

    def _get_errors(self):
        if self._errors is None:
            self._errors = {}
            for name, field in self._fields:
                if field.errors:
                    self._errors[name] = field.errors
        return self._errors
    errors = property(_get_errors)

    def auto_populate(self, model):
        """
        Automatically copy converted form values into the model object.

        This can be very dangerous if not used properly, so make sure to only use
        this in forms with proper validators and the right attributes.
        """
        for name, field in self._fields:
            setattr(model, name, field.data)
