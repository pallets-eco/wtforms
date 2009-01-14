"""
    wtforms.ext.django.orm
    ~~~~~~~~~~~~~~~~~~~~~~
    
    tools for turning django models into a Form.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from wtforms import fields as f
from wtforms import validators
from wtforms import Form
from wtforms.ext.django.fields import ModelSelectField


class ModelConverter(object):
    SIMPLE_CONVERSIONS = {
        # TODO: 'ImageField' 'ManyToManyField' 'NullBooleanField' 'OneToOneField'
        'AutoField': f.IntegerField,
        'BooleanField': f.BooleanField,
        'CharField': f.TextField, 
        'DateTimeField': f.DateTimeField,
        'FileField':  f.FileField,
        'FilePathField': f.FileField,
        'FloatField': f.TextField,
        'IntegerField': f.IntegerField,
        'PhoneNumberField': f.TextField,
        'SmallIntegerField': [f.IntegerField],
        'FloatField': f.TextField,
        'IntegerField': f.IntegerField,
        'PhoneNumberField': f.TextField, # TODO: determine phone number validator?
        'PositiveIntegerField': f.IntegerField,
        'PositiveSmallIntegerField': f.IntegerField,
        'SlugField': f.TextField,
        'TextField': f.TextAreaField,
        'XMLField': f.TextAreaField,
    }

    def convert(self, field):
        kwargs = {
            'label': field.verbose_name,
            'description': field.help_text,
            'validators': [],
            'default': field.default,
        }
        if field.blank:
            kwargs['validators'].append(validators.optional())
        if field.max_length is not None and field.max_length > 0:
            kwargs['validators'].append(validators.length(max=field.max_length))

        fname = type(field).__name__

        if field.choices:
            kwargs['choices'] = field.choices
            return f.SelectField(**kwargs)
        elif fname in self.SIMPLE_CONVERSIONS:
            return self.SIMPLE_CONVERSIONS[fname](**kwargs)
        else:
            m = getattr(self, 'conv_%s' % fname, None)
            if m is not None:
                return m(kwargs, field)

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

def model_form(model, base_class=Form, include_pk=False):
    """
    Create a wtforms form for a given django model class.

    >>> UserForm = model_form(User)

    The form can be made to extend your own form by passing the `base_class` 
    parameter.  The generated form can be subclassed as needed.
    Primary key fields are not included unless you specify include_pk=True.
    """
    meta = model._meta
    f_dict = {}
    converter = ModelConverter()
    for mfield in meta.fields:
        if not include_pk and mfield is meta.pk:
            continue
        mtype = type(mfield).__name__
        formfield = converter.convert(mfield)
        if formfield is not None:
            f_dict[mfield.attname] = formfield
    return type(meta.object_name + 'Form', (base_class, ), f_dict)

__all__ = ('model_form', )
