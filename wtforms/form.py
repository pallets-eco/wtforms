"""
    wtforms.form
    ~~~~~~~~~~~~
    
    The `Form` base class.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from wtforms.validators import StopValidation

class Form(object):
    def __init__(self, formdata=None, obj=None, prefix='', idprefix='', **kwargs):
        if prefix:
            prefix += '_'
        self._idprefix = idprefix

        # populate data from form and optional instance and defaults
        self._errors = None
        self._fields = []
        has_formdata = bool(formdata)
        for name, f in self._unbound_fields:
            form_name = prefix + name
            field = f(_form=self, _name=form_name)
            self._fields.append((name, field))
            setattr(self, name, field)

            field.process_data(field._default, has_formdata)
            if name in kwargs:
                field.process_data(kwargs[name], has_formdata)
            if hasattr(obj, name):
                field.process_data(getattr(obj, name), has_formdata)
            if has_formdata and form_name in formdata:
                try:
                    data = formdata.getlist(form_name)
                except AttributeError:
                    data = formdata.getall(form_name)
                field.process_formdata(data)

    def __new__(cls, *args, **kw):
        """
        Use the field creation counter to create an ordered list of form fields.
        """
        if '_unbound_fields' not in cls.__dict__:
            fields = []
            for name in dir(cls):
                if not name.startswith('_'):
                    field = getattr(cls, name)
                    if  hasattr(field, '_formfield'):
                        fields.append((name, field))
            fields.sort(lambda x,y: cmp(x[1].creation_counter, y[1].creation_counter))
            cls._unbound_fields = fields
        return super(Form, cls).__new__(cls)

    def __iter__(self): 
        for name, field in self._fields:
            yield field

    def __contains__(self, item):
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
        
        Returns True or False.
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
