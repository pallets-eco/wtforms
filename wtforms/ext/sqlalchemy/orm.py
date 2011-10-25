"""
Tools for generating forms based on SQLAlchemy models.
"""
import inspect

from wtforms import fields as f
from wtforms import validators
from wtforms.form import Form


__all__ = (
    'model_fields', 'model_form',
)

def converts(*args):
    def _inner(func):
        func._converter_for = frozenset(args)
        return func
    return _inner

class ModelConverterBase(object):
    def __init__(self, converters, use_mro=True):
        self.use_mro = use_mro

        if not converters:
            converters = {}

        for name in dir(self):
            obj = getattr(self, name)
            if hasattr(obj, '_converter_for'):
                for classname in obj._converter_for:
                    converters[classname] = obj

        self.converters = converters

    def convert(self, model, mapper, prop, field_args):
        if not hasattr(prop, 'columns'):
            # XXX We don't support anything but ColumnProperty at the moment.
            return
        elif len(prop.columns) != 1:
            raise TypeError('Do not know how to convert multiple-column properties currently')

        column = prop.columns[0]

        kwargs = {
            'validators': [],
            'filters': [],
            'default': column.default,
        }
        if field_args:
            kwargs.update(field_args)

        if column.nullable:
            kwargs['validators'].append(validators.Optional())

        if self.use_mro:
            types = inspect.getmro(type(column.type))
        else:
            types = [type(column.type)]

        converter = None
        for col_type in types:
            type_string = '%s.%s' % (col_type.__module__, col_type.__name__)
            if type_string.startswith('sqlalchemy'):
                type_string = type_string[11:]

            if type_string in self.converters:
                converter = self.converters[type_string]
                break
        else:
            for col_type in types:
                if col_type.__name__ in self.converters:
                    converter = self.converters[col_type.__name__]
                    break
            else:
                return
        return converter(model=model, mapper=mapper, prop=prop, column=column, field_args=kwargs)


class ModelConverter(ModelConverterBase):
    def __init__(self, extra_converters=None):
        super(ModelConverter, self).__init__(extra_converters)

    @classmethod
    def _string_common(cls, column, field_args, **extra):
        if column.type.length:
            field_args['validators'].append(validators.Length(max=column.type.length))

    @converts('String', 'Unicode')
    def conv_String(self, field_args, **extra):
        self._string_common(field_args=field_args, **extra)
        return f.TextField(**field_args)

    @converts('Text', 'UnicodeText', 'types.LargeBinary', 'types.Binary')
    def conv_Text(self, field_args, **extra):
        self._string_common(field_args=field_args, **extra)
        return f.TextAreaField(**field_args)

    @converts('Boolean')
    def conv_Boolean(self, field_args, **extra):
        return f.BooleanField(**field_args)

    @converts('Date')
    def conv_Date(self, field_args, **extra):
        return f.DateField(**field_args)

    @converts('DateTime')
    def conv_DateTime(self, field_args, **extra):
        return f.DateTimeField(**field_args)

    @converts('Integer', 'SmallInteger')
    def handle_integer_types(self, column, field_args, **extra):
        unsigned = getattr(column.type, 'unsigned', False)
        if unsigned:
            field_args['validators'].append(validators.NumberRange(min=0))
        return f.IntegerField(**field_args)

    @converts('Numeric', 'Float')
    def handle_decimal_types(self, column, field_args, **extra):
        places = getattr(column.type, 'scale', 2)
        if places is not None:
            field_args['places'] = places
        return f.DecimalField(**field_args)

    @converts('databases.mysql.MSYear')
    def conv_MSYear(self, field_args, **extra):
        field_args['validators'].append(validators.NumberRange(min=1901, max=2155))
        return f.TextField(**field_args)

    @converts('databases.postgres.PGInet', 'dialects.postgresql.base.INET')
    def conv_PGInet(self, field_args, **extra):
        field_args.setdefault('label', u'IP Address')
        field_args['validators'].append(validators.IPAddress())
        return f.TextField(**field_args)


def model_fields(model, only=None, exclude=None, field_args=None, converter=None):
    """
    Generate a dictionary of fields for a given SQLAlchemy model.

    See `model_form` docstring for description of parameters.
    """
    if not hasattr(model, '_sa_class_manager'):
        raise TypeError('model must be a sqlalchemy mapped model')

    mapper = model._sa_class_manager.mapper
    converter = converter or ModelConverter()
    field_args = field_args or {}

    properties = ((p.key, p) for p in mapper.iterate_properties)
    if only:
        properties = (x for x in properties if x[0] in only)
    elif exclude:
        properties = (x for x in properties if x[0] not in exclude)

    field_dict = {}
    for name, prop in properties:
        field = converter.convert(model, mapper, prop, field_args.get(name))
        if field is not None:
            field_dict[name] = field

    return field_dict


def model_form(model, base_class=Form, only=None, exclude=None, field_args=None, converter=None):
    """
    Create a wtforms Form for a given SQLAlchemy model class::

        from wtforms.ext.sqlalchemy.orm import model_form
        from myapp.models import User
        UserForm = model_form(User)

    :param model:
        A SQLAlchemy mapped model class.
    :param base_class:
        Base form class to extend from. Must be a ``wtforms.Form`` subclass.
    :param only:
        An optional iterable with the property names that should be included in
        the form. Only these properties will have fields.
    :param exclude:
        An optional iterable with the property names that should be excluded
        from the form. All other properties will have fields.
    :param field_args:
        An optional dictionary of field names mapping to keyword arguments used
        to construct each field object.
    :param converter:
        A converter to generate the fields based on the model properties. If
        not set, ``ModelConverter`` is used.
    """
    field_dict = model_fields(model, only, exclude, field_args, converter)
    return type(model.__name__ + 'Form', (base_class, ), field_dict)
