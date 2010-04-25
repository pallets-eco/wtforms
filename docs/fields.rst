Fields
======

.. module:: wtforms.fields

Fields are responsible for rendering and data conversion. They delegate to
validators for data validation.

Field definitions
-----------------

Fields are defined as members on a form in a declarative fashion::

    class MyForm(Form):
        name    = TextField(u'Full Name', [validators.required(), validators.length(max=10)])
        address = TextAreaField(u'Mailing Address', [validators.optional(), validators.length(max=200)])

When a field is defined on a form, the construction parameters are saved until
the form is instantiated. At form instantiation time, a copy of the field is 
made with all the parameters specified in the definition. Each instance of the
field keeps its own field data and errors list.

The label and validators can be passed to the constructor as sequential
arguments, while all other arguments should be passed as keyword arguments.
Some fields (such as :class:`SelectField`) can also take additional
field-specific keyword arguments. Consult the built-in fields reference for
information on those.

The Field base class
--------------------

.. class:: Field

    Stores and processes data, and generates HTML for a form field.

    Field instances contain the data of that instance as well as the
    functionality to render it within your Form. They also contain a number of
    properties which can be used within your templates to render the field and
    label.

    **Construction**

    .. automethod:: __init__

    **Validation**

    To validate the field, call its `validate` method, providing a form and any
    extra validators needed. To extend validation behaviour, override
    `pre_validate` or `post_validate`.

    .. automethod:: validate
    .. automethod:: pre_validate
    .. automethod:: post_validate
    .. attribute:: errors

        If `validate` encounters any errors, they will be inserted into this
        list.

    **Data access and processing**

    To handle incoming data from python, override `process_data`. Similarly, to
    handle incoming data from the outside, override `process_formdata`.

    .. automethod:: process(formdata [, data])
    .. automethod:: process_data
    .. automethod:: process_formdata 
    .. attribute:: data

        Contains the resulting (sanitized) value of calling either of the
        process methods. Note that it is not HTML escaped when using in
        templates.

    .. attribute:: raw_data

        If form data is processed, is the valuelist given from the formdata
        wrapper. Otherwise, `raw_data` will be `None`.

    **Rendering**

    To render a field, simply call it, providing any values the widget expects
    as keyword arguments. Usually the keyword arguments are used for extra HTML
    attributes.

    .. automethod:: __call__

        If one wants to pass the "class" argument which is a reserved keyword
        in some python-based templating languages, one can do::

            form.field(class_="text_blob")

        This will output (for a text field):

        .. code-block:: html

            <input type="text" name="field_name" value="blah" class="text_blob" id="field_name" />

        Note: Simply coercing the field to a string or unicode will render it as
        if it was called with no arguments.

    **Properties**

    .. attribute:: name

        The HTML form name of this field. This is the name as defined in your 
        Form prefixed with the `prefix` passed to the Form constructor.

    .. attribute:: short_name

        The un-prefixed name of this field.

    .. attribute:: id

        The HTML ID of this field. If unspecified, this is generated for you to
        be the same as the field name.

    .. attribute:: label

        This is a :class:`Label` instance which when evaluated as a string
        returns an HTML ``<label for="id">`` construct.

    .. attribute:: default

        This is whatever you passed as the `default` to the field's
        constructor, otherwise None.

    .. attribute:: description

        A string containing the value of the description passed in the
        constructor to the field; this is not HTML escaped.

    .. attribute:: errors

       A sequence containing the validation errors for this field.

    .. attribute:: process_errors

       Errors obtained during input processing. These will be prepended to the
       list of errors at validation time.

    .. attribute:: widget

        The widget used to render the field.

    .. attribute:: type

        The type of this field, as a string. This can be used in your templates
        to do logic based on the type of field:

        .. code-block:: html+django

            {% for field in form %}
                <tr>
                {% if field.type == "BooleanField" %}
                    <td></td>
                    <td>{{ field }} {{ field.label }}</td>
                {% else %}
                    <td>{{ field.label }}</td>
                    <td>{{ field }}</td>
                {% end %}
                </tr>
            {% endfor %}

    .. attribute:: flags

        An object containing boolean flags set either by the field itself, or
        by validators on the field. For example, the built-in
        :class:`~wtforms.validators.Required` validator sets the `required` flag.
        An unset flag will result in :const:`False`.

        .. code-block:: html+django

            {% for field in form %}
                <tr>
                    <th>{{ field.label }} {% if field.flags.required %}*{% endif %}</th>
                    <td>{{ field }}</td>
                </tr>
            {% endfor %}

Basic fields
------------

Basic fields generally represent scalar data types with single values, and
refer to a single input from the form.

.. autoclass:: BooleanField(default field arguments)

.. autoclass:: DateField(default field arguments, format='%Y-%m-%d')

.. autoclass:: DateTimeField(default field arguments, format='%Y-%m-%d %H:%M:%S')

  For better date/time fields, see the :mod:`dateutil extension <wtforms.ext.dateutil.fields>`

.. autoclass:: DecimalField(default field arguments, places=2, rounding=None)

.. autoclass:: FileField(default field arguments)

    Example usage::

        class UploadForm(Form):
            image        = FileField(u'Image File', [validators.regexp(u'^[^/\\]\.jpg$')])
            description  = TextAreaField(u'Image Description')

            def validate_image(form, field):
                if field.data:
                    field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)

        def upload(request):
            form = UploadForm(request.POST)
            if form.image.data:
                image_data = request.FILES[form.image.name].read()
                open(os.path.join(UPLOAD_PATH, form.image.data), 'w').write(image_data)

.. autoclass:: FloatField(default field arguments)

   For the majority of uses, :class:`DecimalField` is preferable to FloatField,
   except for in cases where an IEEE float is absolutely desired over a decimal
   value.

.. autoclass:: HiddenField(default field arguments)

    HiddenField is useful for providing data from a model or the application to
    be used on the form handler side for making choices or finding records.
    Very frequently, CRUD forms will use the hidden field for an object's id.   

    Hidden fields are like any other field in that they can take validators and
    values and be accessed on the form object.   You should consider validating
    your hidden fields just as you'd validate an input field, to prevent from
    malicious people playing with your data.

.. autoclass:: IntegerField(default field arguments)

.. autoclass:: PasswordField(default field arguments)

    Other than the fact that this makes a password input field, this field
    functions exactly like a text-input field.

.. autoclass:: RadioField(default field arguments, choices=[], coerce=unicode)

    .. code-block:: jinja

        {% for subfield in form.radio %}
            <tr>
                <td>{{ subfield }}</td>
                <td>{{ subfield.label }}</td>
            </tr>
        {% endfor %}

    Simply outputting the field without iterating its subfields will result in
    a ``<ul>`` list of radio choices.

.. class:: SelectField(default field arguments, choices=[], coerce=unicode, option_widget=None)

    Select fields keep a `choices` property which is a sequence of `(value,
    label)` pairs.  The value portion can be any type in theory, but as form
    data is sent by the browser as strings, you will need to provide a function
    which can coerce the string representation back to a comparable object.

    **Select fields with static choice values**::

        class PastebinEntry(Form):
            language = SelectField(u'Programming Language', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])

    Note that the `choices` keyword is only evaluated once, so if you want to make
    a dynamic drop-down list, you'll want to assign the choices list to the field
    after instantiation.

    **Select fields with dynamic choice values**::

        class UserDetails(Form):
            group_id = SelectField(u'Group', coerce=int)

        def edit_user(request, id):
            user = User.query.get(id)
            form = UserDetails(request.POST, obj=user)
            form.group_id.choices = [(g.id, g.name) for g in Group.query.order_by('name')]

    Note we didn't pass a `choices` to the :class:`~wtforms.fields.SelectField` 
    constructor, but rather created the list in the view function. Also, the 
    `coerce` keyword arg to :class:`~wtforms.fields.SelectField` says that we 
    use :func:`int()` to coerce form data.  The default coerce is 
    :func:`unicode()`. 

    **Advanced functionality**

    SelectField and its descendants are iterable, and iterating it will produce
    a list of fields each representing an option. The rendering of this can be
    further controlled by specifying `option_widget=`.

.. autoclass:: SelectMultipleField(default field arguments, choices=[], coerce=unicode, option_widget=None)

   The data on the SelectMultipleField is stored as a list of objects, each of
   which is checked and coerced from the form input.  Any inputted choices
   which are not in the given choices list will cause validation on the field
   to fail.

.. autoclass:: SubmitField(default field arguments)

.. autoclass:: TextAreaField(default field arguments)

    .. code-block: jinja

        {{ form.textarea(rows=7, cols=90) }}

.. autoclass:: TextField(default field arguments)

   .. code-block:: jinja

        {{ form.username(size=30, maxlength=50) }}

Field Enclosures
----------------

Field enclosures allow you to have fields which represent a collection of
fields, so that a form can be composed of multiple re-usable components or more
complex data structures such as lists and nested objects can be represented.

.. autoclass:: FormField(form_class, default field arguments, separator='-')

    FormFields are useful for editing child objects or enclosing multiple
    related forms on a page which are submitted and validated together.  While
    subclassing forms captures most desired behaviours, sometimes for
    reusability or purpose of combining with `FieldList`, FormField makes
    sense.

    For example, take the example of a contact form which uses a similar set of
    three fields to represent telephone numbers::

        class TelephoneForm(Form):
            country_code = IntegerField('Country Code', [validators.required()])
            area_code    = IntegerField('Area Code/Exchange', [validators.required()])
            number       = TextField('Number')

        class ContactForm(Form):
            first_name   = TextField()
            last_name    = TextField()
            mobile_phone = FormField(TelephoneForm)
            office_phone = FormField(TelephoneForm)

    In the example, we reused the TelephoneForm to encapsulate the common
    telephone entry instead of writing a custom field to handle the 3
    sub-fields. The `data` property of the mobile_phone field will return the
    :attr:`~wtforms.form.Form.data` dict of the enclosed form. Similarly, the 
    `errors` property encapsulate the forms' errors.

.. autoclass:: FieldList(unbound_field, default field arguments, min_entries=0, max_entries=None)

    **Note**: Due to a limitation in how HTML sends values, FieldList cannot enclose 
    :class:`BooleanField` or :class:`SubmitField` instances.

    :class:`FieldList` is not limited to enclosing simple fields; and can
    indeed represent a list of enclosed forms by combining FieldList with
    FormField::

        class IMForm(Form):
            protocol = SelectField(choices=[('aim', 'AIM'), ('msn', 'MSN')])
            username = TextField()

        class ContactForm(Form):
            first_name  = TextField()
            last_name   = TextField()
            im_accounts = FieldList(FormField(IMForm))


Custom Fields
-------------

While WTForms provides customization for existing fields using widgets and
keyword argument attributes, sometimes it is necessary to design custom fields
to handle special data types in your application.

Let's design a field which represents a comma-separated list of tags::

    class TagListField(Field):
        widget = TextInput()

        def _value(self):
            if self.data:
                return u', '.join(self.data)
            else:
                return u''

        def process_formdata(self, valuelist):
            if valuelist:
                self.data = [x.strip() for x in valuelist[0].split(',')]
            else:
                self.data = []

The `_value` method is called by the :class:`~wtforms.widgets.TextInput` widget
to provide the value that is displayed in the form. Overriding the
:meth:`~Field.process_formdata` method processes the incoming form data back
into a list of tags.


Fields With Custom Constructors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Custom fields can also override the default field constructor if needed to
provide additional customization::

    class BetterTagListField(TagListField):
        def __init__(self, label='', validators=None, remove_duplicates=True, **kwargs):
            super(BetterTagListField, self).__init__(label, validators, **kwargs)
            self.remove_duplicates = remove_duplicates

        def process_formdata(self, valuelist):
            super(BetterTagListField, self).process_formdata(valuelist)
            if self.remove_duplicates:
                self.data = list(self._remove_duplicates(self.data))

        @classmethod
        def _remove_duplicates(cls, seq):
            """Remove duplicates in a case insensitive, but case preserving manner"""
            d = {}
            for item in seq:
                if item.lower() not in d:
                    d[item.lower()] = True
                    yield item

When you override a Field's constructor, to maintain consistent behavior, you
should design your constructor so that:

 * You take `label='', validators=None` as the first two positional arguments
 * Add any additional arguments your field takes as keyword arguments after the
   label and validators
 * Take `**kwargs` to catch any additional keyword arguments.
 * Call the Field constructor first, passing the first two positional
   arguments, and all the remaining keyword args.


Considerations for overriding process()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the vast majority of fields, it is not necessary to override
:meth:`Field.process`. Most of the time, you can achieve what is needed by
overriding ``process_data`` and/or ``process_formdata``. However, for special
types of fields, such as form enclosures and other special cases of handling
multiple values, it may be needed.

If you are going to override ``process()``, be careful about how you deal with
the ``formdata`` parameter. For compatibility with the maximum number of
frameworks, we suggest you limit yourself to manipulating formdata in the
following ways only:

* Testing emptiness: ``if formdata``
* Checking for key existence: ``key in formdata``
* Iterating all keys: ``for key in formdata`` (note that some wrappers may
  return multiple instances of the same key)
* Getting the list of values for a key: ``formdata.getlist(key)``.

Most importantly, you should not use dictionary-style access to work with your
formdata wrapper, because the behavior of this is highly variant on the
wrapper: some return the first item, others return the last, and some may
return a list.
