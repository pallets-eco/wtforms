__all__ = (
    'BaseForm',
    'Form',
)

class BaseForm(object):
    """
    Base Form Class.  Provides core behaviour like field construction,
    validation, and data and error proxying.
    """

    def __init__(self, fields, prefix=''):
        """
        :param unbound_fields:
            A dict which maps field names to UnboundField instances.
        :param prefix:
            If provided, all fields will have their name prefixed with the
            value.
        """
        if prefix:
            prefix += '-'

        self._errors = None
        self._fields = {}

        for name, unbound_field in fields.iteritems():
            field = unbound_field.bind(form=self, name=name, prefix=prefix)
            self._fields[name] = field

    def __iter__(self):
        """ Iterate form fields in arbitrary order"""
        return self._fields.itervalues()

    def __contains__(self, item):
        """ Returns `True` if the named field is a member of this form. """
        return (item in self._fields)

    def __getitem__(self, name):
        """ Dict-style access to this form's fields."""
        return self._fields[name]

    def __setitem__(self, name, value):
        self._fields[name] = value

    def __delitem__(self, name):
        del self._fields[name]

    def __getattr__(self, name):
        try:
            return self._fields[name]
        except KeyError:
            raise AttributeError('Form has no field %r' % name)

    def __delattr__(self, name):
        try:
            del self._fields[name]
        except KeyError:
            super(BaseForm, self).__delattr__(name)

    def populate_obj(self, obj):
        """
        Populates the attributes of the passed `obj` with data from the form's
        fields.

        :note: This is a destructive operation; Any attribute with the same name
               as a field will be overridden. Use with caution.
        """
        for name, field in self._fields.iteritems():
            field.populate_obj(obj, name)

    def process(self, formdata=None, obj=None, **kwargs):
        """
        :param formdata:
            Used to pass data coming from the enduser, usually `request.POST` or
            equivalent.
        :param obj:
            If `formdata` has no data for a field, the form will try to get it
            from the passed object.
        :param `**kwargs`:
            If neither `formdata` or `obj` contains a value for a field, the
            form will assign the value of a matching keyword argument to the
            field, if provided.
        """
        if not formdata:
            # XXX This is only because Field.process checks for None, which it
            # really shouldn't
            formdata = None
        for name, field, in self._fields.iteritems():
            if hasattr(obj, name):
                field.process(formdata, getattr(obj, name))
            elif name in kwargs:
                field.process(formdata, kwargs[name])
            else:
                field.process(formdata)

    def validate(self):
        """
        Validates the form by calling `validate` on each field, passing any
        extra `Form.validate_<fieldname>` validators to the field validator.

        Returns `True` if no errors occur.
        """
        self._errors = None
        success = True
        for name, field in self._fields.iteritems():
            extra = []
            inline = getattr(self.__class__, 'validate_%s' % name, None)
            if inline is not None:
                extra.append(inline)
            if not field.validate(self, extra):
                success = False
        return success

    @property
    def data(self):
        return dict((name, f.data) for name, f in self._fields.iteritems())

    @property
    def errors(self):
        if self._errors is None:
            self._errors = dict((name, f.errors) for name, f in self._fields.iteritems() if f.errors)
        return self._errors


class FormMeta(type):
    """
    The metaclass for `Form` and any subclasses of `Form`.

    `FormMeta`'s responsibility is to create the `_unbound_fields` list, which
    is a list of `UnboundField` instances sorted by their order of
    instantiation.  The list is created at the first instantiation of the form.
    If any fields are added/removed from the form, the list is cleared to be
    re-generated on the next instantiaton.

    Any properties which begin with an underscore or are not `UnboundField`
    instances are ignored by the metaclass.
    """
    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)
        cls._unbound_fields = None

    def __call__(cls, *args, **kwargs):
        """
        Construct a new `Form` instance, creating `_unbound_fields` on the
        class if it is empty.
        """
        if cls._unbound_fields is None:
            fields = []
            for name in dir(cls):
                if not name.startswith('_'):
                    unbound_field = getattr(cls, name)
                    if hasattr(unbound_field, '_formfield'):
                        fields.append((name, unbound_field))
            # We keep the name as the second element of the sort
            # to ensure a stable sort.
            fields.sort(key=lambda x: (x[1].creation_counter, x[0]))
            cls._unbound_fields = fields
        return type.__call__(cls, *args, **kwargs)

    def __setattr__(cls, name, value):
        """
        Add an attribute to the class, clearing `_unbound_fields` if needed.
        """
        if not name.startswith('_') and hasattr(value, '_formfield'):
            cls._unbound_fields = None
        type.__setattr__(cls, name, value)

    def __delattr__(cls, name):
        """
        Remove an attribute from the class, clearing `_unbound_fields` if
        needed.
        """
        if not name.startswith('_'):
            cls._unbound_fields = None
        type.__delattr__(cls, name)


class Form(BaseForm):
    """
    Declarative Form base class. Extends BaseForm's core behaviour allowing
    fields to be defined on Form subclasses as class attributes.

    In addition, form and instance input data are taken at construction time
    and passed to `process()`.
    """
    __metaclass__ = FormMeta

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        """
        :param formdata:
            Used to pass data coming from the enduser, usually `request.POST` or
            equivalent.
        :param obj:
            If `formdata` has no data for a field, the form will try to get it
            from the passed object.
        :param prefix:
            If provided, all fields will have their name prefixed with the
            value.
        :param `**kwargs`:
            If neither `formdata` or `obj` contains a value for a field, the
            form will assign the value of a matching keyword argument to the
            field, if provided.
        """
        super(Form, self).__init__(dict(self._unbound_fields), prefix=prefix)

        for name in self._fields:
            # Set all the fields to attributes so that they obscure the class
            # attributes with the same names.
            setattr(self, name, self._fields[name])

        self.process(formdata, obj, **kwargs)

    def __iter__(self):
        """ Iterate form fields in their order of definition on the form. """
        for name, _ in self._unbound_fields:
            yield self._fields[name]

    def __delattr__(self, name):
        super(Form, self).__delattr__(name)
        setattr(self, name, None)
