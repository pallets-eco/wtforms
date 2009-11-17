"""
Tools for generating forms based on Django models.
"""
from wtforms import fields as f
from wtforms import Form
from wtforms import validators
from wtforms.ext.django.fields import ModelSelectField


__all__ = (
    'model_form',
)


class ModelConverter(object):
    SIMPLE_CONVERSIONS = {
        # TODO: 'ImageField' 'ManyToManyField' 'OneToOneField'
        'AutoField': f.IntegerField,
        'BooleanField': f.BooleanField,
        'CharField': f.TextField,
        'DateTimeField': f.DateTimeField,
        'FileField':  f.FileField,
        'FilePathField': f.FileField,
        'FloatField': f.TextField,
        'IntegerField': f.IntegerField,
        'PhoneNumberField': f.TextField,
        'SmallIntegerField': f.IntegerField,
        'FloatField': f.TextField,
        'IntegerField': f.IntegerField,
        'PositiveIntegerField': f.IntegerField,
        'PositiveSmallIntegerField': f.IntegerField,
        'SlugField': f.TextField,
        'TextField': f.TextAreaField,
        'XMLField': f.TextAreaField,
    }

    def convert(self, model, field, field_args):
        kwargs = {
            'label': field.verbose_name,
            'description': field.help_text,
            'validators': [],
            'default': field.default,
        }
        if field_args:
            kwargs.update(field_args)

        if field.blank:
            kwargs['validators'].append(validators.Optional())
        if field.max_length is not None and field.max_length > 0:
            kwargs['validators'].append(validators.Length(max=field.max_length))

        if field.choices:
            kwargs['choices'] = field.choices
            return f.SelectField(**kwargs)
        else:
            ftype = type(field).__name__
            converter = getattr(self, 'conv_%s' % ftype, None)
            if converter is not None:
                return converter(kwargs, field)
            elif ftype in self.SIMPLE_CONVERSIONS:
                return self.SIMPLE_CONVERSIONS[ftype](**kwargs)

    def conv_ForeignKey(self, kwargs, field):
        return ModelSelectField(model=field.rel.to, **kwargs)

    def conv_TimeField(self, kwargs, field):
        return f.DateTimeField(format='%H-%M-%S', **kwargs)

    def conv_DateField(self, kwargs, field):
        return f.DateTimeField(format='%Y-%m-%d', **kwargs)

    def conv_EmailField(self, kwargs, field):
        kwargs['validators'].append(validators.email())
        return f.TextField(**kwargs)

    def conv_IPAddressField(self, kwargs, field):
        kwargs['validators'].append(validators.ip_address())
        return f.TextField(**kwargs)

    def conv_URLField(self, kwargs, field):
        kwargs['validators'].append(validators.url())
        return f.TextField(**kwargs)

    def conv_USStateField(self, kwargs, field):
        try:
            from django.contrib.localflavor.us.us_states import STATE_CHOICES
        except ImportError:
            STATE_CHOICES = []

        return f.SelectField(choices=STATE_CHOICES, **kwargs)

    def conv_NullBooleanField(self, kwargs, field):
        def coerce_nullbool(value):
            d = {'None': None, None: None, 'True': True, 'False': False}
            if value in d:
                return d[value]
            else:
                return bool(int(value))

        choices = ((None, 'Unknown'), (True, 'Yes'), (False, 'No'))
        return f.SelectField(choices=choices, coerce=coerce_nullbool, **kwargs)

def model_fields(model, only=None, exclude=None, field_args=None, converter=None):
    """
    Generate a dictionary of fields for a given Django model.

    See `model_form` docstring for description of parameters.
    """
    converter = converter or ModelConverter()
    field_args = field_args or {}

    model_fields = ((f.attname, f) for f in model._meta.fields)
    if only:
        model_fields = (x for x in model_fields if x[0] in only)
    elif exclude:
        model_fields = (x for x in model_fields if x[0] not in exclude)

    field_dict = {}
    for name, model_field in model_fields:
        field = converter.convert(model, model_field, field_args.get(name))
        if field is not None:
            field_dict[name] = field

    return field_dict

def model_form(model, base_class=Form, only=None, exclude=None, field_args=None, converter=None):
    """
    Create a wtforms Form for a given Django model class::

        from wtforms.ext.django.orm import model_form
        from myproject.myapp.models import User
        UserForm = model_form(User)

    :param model:
        A Django ORM model class
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
    return type(model._meta.object_name + 'Form', (base_class, ), field_dict)
