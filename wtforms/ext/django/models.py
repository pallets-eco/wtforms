from wtforms import fields as f
from wtforms import validators
from wtforms import Form

# Mapping is Django Field : [wtforms_field_class, options_dict, validators]
FIELDS_MAP = {
    # ForeignKey: [f.SelectField],
    'AutoField': [f.IntegerField],
    'BooleanField': [f.BooleanField],
    'DateField': [f.DateTimeField, {'format': '%Y-%m-%d'}],
    'DateTimeField': [f.DateTimeField],
    'EmailField': [f.TextField, {}, validators.email()],
    # 'FileField:  [f.FileField],
    'FilePathField': [f.FileField],
    'FloatField': [f.TextField],
    'IPAddressField': [f.TextField, {}, validators.ip_address()],
    # 'ImageField
    'IntegerField': [f.IntegerField],
    # 'ManyToManyField
    # 'NullBooleanField
    # 'OneToOneField
    'PhoneNumberField': [f.TextField], # TODO: determine phone number validator?
    'PositiveIntegerField': [f.IntegerField],
    'PositiveSmallIntegerField': [f.IntegerField],
    'SlugField': [f.TextField],
    'SmallIntegerField': [f.IntegerField],
    'TextField': [f.TextAreaField],
    'TimeField': [f.DateTimeField, {'format': '%Y-%m-%d'}],
    'URLField': [f.TextField],
    'USStateField': [f.TextField],
    # 'XMLField
}

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
    for mfield in meta.fields:
        if not include_pk and mfield is meta.pk:
            continue
        mtype = type(mfield).__name__
        if mtype in FIELDS_MAP:
            field_spec = FIELDS_MAP[mtype]
            # TODO: use field.blank to form the basis for 'required' value once we implement it.
            if len(field_spec) > 1:
                kwargs = field_spec[1] 
            else:
                kwargs = {}
            formfield = field_spec[0](unicode(mfield.verbose_name), validators=field_spec[2:], **kwargs)
            f_dict[mfield.attname] = formfield
    return type(meta.object_name + 'Form', (base_class, ), f_dict)
