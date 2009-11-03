__all__ = (
    'Form',
)


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


class Form(object):
    """
    Form base class. Provides core behaviour like field construction,
    validation, and data and error proxying.
    """
    __metaclass__ = FormMeta

    def __init__(self, formdata=None, obj=None, prefix='', idprefix='', **kwargs):
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
        :param idprefix:
            If provided, prefixes the id's of all fields with the value.
        :param `**kwargs`:
            If neither `formdata` or `obj` contains a value for a field, the
            form will assign the value of a matching keyword argument to the
            field, if provided.
        """
        if prefix:
            prefix += '-'
        self._idprefix = idprefix

        # populate data from form and optional instance and defaults
        self._errors = None
        self._fields = []
        if not formdata:
            formdata = None
        for name, unbound_field in self._unbound_fields:
            field = unbound_field.bind(form=self, name=prefix + name)
            if not field.label.text:
                field.label.text = name.replace('_', ' ').title()
            self._fields.append((name, field))
            setattr(self, name, field)

            if hasattr(obj, name):
                field.process(formdata, getattr(obj, name))
            elif name in kwargs:
                field.process(formdata, kwargs[name])
            else:
                field.process(formdata)

    def __iter__(self):
        """ Iterate form fields in their order of definition on the form. """
        for name, field in self._fields:
            yield field

    def __contains__(self, item):
        """ Returns `True` if the named field is a member of this form. """
        return getattr(getattr(self, item, False), '_formfield', False) is True

    def __delattr__(self, name):
        try:
            self._fields.remove((name, getattr(self, name)))
            setattr(self, name, None)
        except ValueError:
            super(Form, self).__delattr__(name)

    def __getitem__(self, name):
        """ Dict-style access to this form for frameworks which need it. """
        try:
            return getattr(self, name)
        except AttributeError:
            raise KeyError(name)

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

    @property
    def data(self):
        data = {}
        for name, field in self._fields:
            data[name] = field.data
        return data

    @property
    def errors(self):
        if self._errors is None:
            self._errors = {}
            for name, field in self._fields:
                if field.errors:
                    self._errors[name] = field.errors
        return self._errors

    def populate_obj(self, obj):
        """
        Populates the attributes of the passed `obj` with data from the form's
        fields.

        :note: This is a destructive operation; Any attribute with the same name
               as a field will be overridden. Use with caution.
        """
        for name, field in self._fields:
            field.populate_obj(obj, name)
