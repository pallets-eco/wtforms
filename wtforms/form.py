"""
    wtforms.form
    ~~~~~~~~~~~~
    
    TODO
    
    :copyright: 2007-2008 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from wtforms.validators import StopValidation

class Form(object):
    def __init__(self, formdata=None, obj=None, prefix='', idprefix='', **kwargs):
        if prefix:
            prefix += '_'
        self._idprefix = idprefix

        # populate data from form and optional instance and defaults
        self.errors = {}
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
        return super(Form, cls).__new__(cls, *args, **kw)

    def __iter__(self): 
        for name, field in self._fields:
            yield field

    def __delattr__(self, name): 
        try: 
            self._fields.remove((name, getattr(self, name)))
            setattr(self, name, None)
        except ValueError:
            super(Form, self).__delattr__(name)

    def validate(self):
        success = True
        for name, field in self._fields:
            field.errors = []
            validators = list(field.validators)
            validators.append(field._validate)
            inline_validator = getattr(self.__class__, 'validate_%s' % name, None)
            if inline_validator is not None:
                validators.append(inline_validator)
            for validator in validators:
                try:
                    validator(self, field)
                except StopValidation, e:
                    if e.args and e.args[0]:
                        field.errors.append(e.args[0])
                    break
                except ValueError, e:
                    field.errors.append(e.args[0])
            if field.errors:
                success = False
                self.errors[name] = field.errors
        return success

    def _get_data(self):
        data = {}
        for name, field in self._fields:
            data[name] = field.data
        return data
    data = property(_get_data)

    def auto_populate(self, model):
        """
        Automatically copy converted form values into the model object.

        This can be very dangerous if not used properly, so make sure to only use
        this in forms with proper validators and the right attributes.
        """
        for name, field in self._fields:
            setattr(model, name, field.data)
