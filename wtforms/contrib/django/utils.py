from django.db import models as m
from wtforms import fields as f
from wtforms import validators
from wtforms import Form

# Mapping is Django Model : [wtforms_field_class, options_dict, validators]
FIELDS_MAP = {
    # m.ForeignKey: [f.SelectField],
    m.AutoField: [f.IntegerField],
    m.BooleanField: [f.BooleanField],
    m.DateField: [f.DateTimeField, {'format': '%Y-%m-%d'}],
    m.DateTimeField: [f.DateTimeField],
    m.EmailField: [f.TextField, {}, validators.email],
    # m.FileField:  [f.FileField],
    m.FilePathField: [f.FileField],
    m.FloatField: [f.TextField],
    m.IPAddressField: [f.TextField, {}, validators.ip_address],
    # m.ImageField
    m.IntegerField: [f.IntegerField],
    # m.ManyToManyField
    # m.NullBooleanField
    # m.OneToOneField
    m.PhoneNumberField: [f.TextField], # TODO: determine phone number validator?
    m.PositiveIntegerField: [f.IntegerField],
    m.PositiveSmallIntegerField: [f.IntegerField],
    m.SlugField: [f.TextField],
    m.SmallIntegerField: [f.IntegerField],
    m.TextField: [f.TextAreaField],
    m.TimeField: [f.DateTimeField, {'format': '%Y-%m-%d'}],
    m.URLField: [f.TextField],
    m.USStateField: [f.TextField],
    # m.XMLField
}

def form_for_model(model, base_class=Form, include_pk=False):
    """
    Create a wtforms form for a given django model class.

    >>> UserForm = form_for_model(User)

    The form can be made to extend your own form by passing the `base_class` 
    parameter.  The generated form can be subclassed as needed.
    Primary key fields are not included unless you specify include_pk=True.
    """
    meta = model._meta
    f_dict = {}
    for mfield in meta.fields:
        if not include_pk and mfield is meta.pk:
            continue
        mtype = type(mfield)
        if mtype in FIELDS_MAP:
            field_spec = FIELDS_MAP[mtype]
            # TODO: use field.blank to form the basis for 'required' value once we implement it.
            if len(field_spec) > 1:
                kwargs = field_spec[1] 
            else:
                kwargs = {}
            formfield = field_spec[0](unicode(mfield.verbose_name), *field_spec[2:], **kwargs)
            f_dict[mfield.attname] = formfield
    return type(meta.object_name + 'Form', (base_class, ), f_dict)
