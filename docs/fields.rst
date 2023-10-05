Fields
======

.. module:: wtforms.fields

Fields are responsible for rendering and data conversion. They delegate to
validators for data validation.

Field definitions
-----------------

Fields are defined as members on a form in a declarative fashion::

    class MyForm(Form):
        name    = StringField('Full Name', [validators.required(), validators.length(max=10)])
        address = TextAreaField('Mailing Address', [validators.optional(), validators.length(max=200)])

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

    .. attribute:: object_data

        This is the data passed from an object or from kwargs to the field,
        stored unmodified. This can be used by templates, widgets, validators
        as needed (for comparison, for example)

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

        Note: Simply coercing the field to a string will render it as
        if it was called with no arguments.

    .. automethod:: __html__

        Many template engines use the __html__ method when it exists on a
        printed object to get an 'html-safe' string that will not be
        auto-escaped. To allow for printing a bare field without calling it,
        all WTForms fields implement this method as well.

    **Message Translations**

    .. automethod:: gettext

    .. automethod:: ngettext

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
       :noindex:

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
                {% endif %}
                </tr>
            {% endfor %}

    .. attribute:: flags

        An object containing flags set either by the field itself, or
        by validators on the field. For example, the built-in
        :class:`~wtforms.validators.InputRequired` validator sets the `required` flag.
        An unset flag will result in :const:`None`.

        .. code-block:: html+django

            {% for field in form %}
                <tr>
                    <th>{{ field.label }} {% if field.flags.required %}*{% endif %}</th>
                    <td>{{ field }}</td>
                </tr>
            {% endfor %}

    .. attribute:: meta

        The same :doc:`meta object <meta>` instance as is available as
        :attr:`Form.meta <wtforms.form.Form.meta>`


    .. attribute:: filters

        The same sequence of filters that was passed as the ``filters=`` to
        the field constructor. This is usually a sequence of callables.


Basic fields
------------

Basic fields generally represent scalar data types with single values, and
refer to a single input from the form.

.. autoclass:: BooleanField(default field arguments, false_values=None)

.. autoclass:: DateField(default field arguments, format='%Y-%m-%d')

.. autoclass:: DateTimeField(default field arguments, format='%Y-%m-%d %H:%M:%S')

.. autoclass:: DateTimeLocalField(default field arguments, format='%Y-%m-%d %H:%M:%S')

.. autoclass:: DecimalField(default field arguments, places=2, rounding=None, use_locale=False, number_format=None)

.. autoclass:: DecimalRangeField(default field arguments)

.. autoclass:: EmailField(default field arguments)

.. autoclass:: FileField(default field arguments)

    Example usage::

        class UploadForm(Form):
            image        = FileField('Image File', [validators.regexp('^[^/\\]\.jpg$')])
            description  = TextAreaField('Image Description')

            def validate_image(form, field):
                if field.data:
                    field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)

        def upload(request):
            form = UploadForm(request.POST)
            if form.image.data:
                image_data = request.FILES[form.image.name].read()
                open(os.path.join(UPLOAD_PATH, form.image.data), 'w').write(image_data)

.. autoclass:: MultipleFileField(default field arguments)

.. autoclass:: FloatField(default field arguments)

   For the majority of uses, :class:`DecimalField` is preferable to FloatField,
   except for in cases where an IEEE float is absolutely desired over a decimal
   value.

.. autoclass:: IntegerField(default field arguments)

.. autoclass:: IntegerRangeField(default field arguments)

.. autoclass:: MonthField(default field arguments, format='%Y:%m')

.. autoclass:: RadioField(default field arguments, choices=[], coerce=str)

    .. code-block:: jinja

        {% for subfield in form.radio %}
            <tr>
                <td>{{ subfield }}</td>
                <td>{{ subfield.label }}</td>
            </tr>
        {% endfor %}

    Simply outputting the field without iterating its subfields will result in
    a ``<ul>`` list of radio choices.

.. class:: SelectField(default field arguments, choices=[], coerce=str, option_widget=None, validate_choice=True)

    Select fields take a ``choices`` parameter which is either:

    * a list of ``(value, label)`` or ``(value, label, render_kw)`` tuples.
      It can also be a list of only values, in which case the value is used
      as the label. If set, the ``render_kw`` dictionnary will be rendered as
      HTML ``<option>`` parameters. The value can be of any
      type, but because form data is sent to the browser as strings, you
      will need to provide a ``coerce`` function that converts a string
      back to the expected type.
    * a dictionary of ``{label: list}`` pairs defining groupings of options.
    * a function taking no argument, and returning either a list or a dictionary.


    **Select fields with static choice values**::

        class PastebinEntry(Form):
            language = SelectField('Programming Language', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])

    Note that the `choices` keyword is only evaluated once, so if you want to make
    a dynamic drop-down list, you'll want to assign the choices list to the field
    after instantiation. Any submitted choices which are not in the given choices
    list will cause validation on the field to fail. If this option cannot be
    applied to your problem you may wish to skip choice validation (see below).

    **Select fields with dynamic choice values**::

        class UserDetails(Form):
            group_id = SelectField('Group', coerce=int)

        def edit_user(request, id):
            user = User.query.get(id)
            form = UserDetails(request.POST, obj=user)
            form.group_id.choices = [(g.id, g.name) for g in Group.query.order_by('name')]

    Note we didn't pass a `choices` to the :class:`~wtforms.fields.SelectField`
    constructor, but rather created the list in the view function. Also, the
    `coerce` keyword arg to :class:`~wtforms.fields.SelectField` says that we
    use :func:`int()` to coerce form data.  The default coerce is
    :func:`str()`.

    **Coerce function example**::

        def coerce_none(value):
            if value == 'None':
                return None
            return value

        class NonePossible(Form):
            my_select_field = SelectField('Select an option', choices=[('1', 'Option 1'), ('2', 'Option 2'), ('None', 'No option')], coerce=coerce_none)

    Note when the option None is selected a 'None' str will be passed. By using a coerce
    function the 'None' str will be converted to None.

    **Skipping choice validation**::

        class DynamicSelectForm(Form):
            dynamic_select = SelectField("Choose an option", validate_choice=False)

    Note the `validate_choice` parameter - by setting this to :const:`False` we
    are telling the SelectField to skip the choice validation step and instead
    to accept any inputted choice without checking to see if it was one of the
    given choices. This should only really be used in situations where you
    cannot use dynamic choice values as shown above - for example where the
    choices of a :class:`~wtforms.fields.SelectField` are determined
    dynamically by another field on the page, such as choosing a country and
    state/region.

    **Advanced functionality**

    SelectField and its descendants are iterable, and iterating it will produce
    a list of fields each representing an option. The rendering of this can be
    further controlled by specifying `option_widget=`.

.. autoclass:: SearchField(default field arguments)

.. autoclass:: SelectMultipleField(default field arguments, choices=[], coerce=str, option_widget=None)

   The data on the SelectMultipleField is stored as a list of objects, each of
   which is checked and coerced from the form input.  Any submitted choices
   which are not in the given choices list will cause validation on the field
   to fail.

.. autoclass:: SubmitField(default field arguments)

.. autoclass:: StringField(default field arguments)

   .. code-block:: jinja

        {{ form.username(size=30, maxlength=50) }}

.. autoclass:: TelField(default field arguments)

.. autoclass:: TimeField(default field arguments, format='%H:%M')

.. autoclass:: URLField(default field arguments)


Convenience Fields
------------------

.. autoclass:: HiddenField(default field arguments)

    HiddenField is useful for providing data from a model or the application to
    be used on the form handler side for making choices or finding records.
    Very frequently, CRUD forms will use the hidden field for an object's id.

    Hidden fields are like any other field in that they can take validators and
    values and be accessed on the form object.   You should consider validating
    your hidden fields just as you'd validate an input field, to prevent from
    malicious people playing with your data.

.. autoclass:: PasswordField(default field arguments)

.. autoclass:: TextAreaField(default field arguments)

    .. code-block: jinja

        {{ form.textarea(rows=7, cols=90) }}

.. autoclass:: ColorField(default field arguments)


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
            number       = StringField('Number')

        class ContactForm(Form):
            first_name   = StringField()
            last_name    = StringField()
            mobile_phone = FormField(TelephoneForm)
            office_phone = FormField(TelephoneForm)

    In the example, we reused the TelephoneForm to encapsulate the common
    telephone entry instead of writing a custom field to handle the 3
    sub-fields. The `data` property of the mobile_phone field will return the
    :attr:`~wtforms.form.Form.data` dict of the enclosed form. Similarly, the
    `errors` property encapsulate the forms' errors.

.. autoclass:: FieldList(unbound_field, default field arguments, min_entries=0, max_entries=None, separator='-')

    **Note**: Due to a limitation in how HTML sends values, FieldList cannot enclose
    :class:`BooleanField` or :class:`SubmitField` instances.

    .. automethod:: append_entry([data])
    .. automethod:: pop_entry

    .. attribute:: entries

        Each entry in a FieldList is actually an instance of the field you
        passed in. Iterating, checking the length of, and indexing the
        FieldList works as expected, and proxies to the enclosed entries list.

        **Do not** resize the entries list directly, this will result in
        undefined behavior. See `append_entry` and `pop_entry` for ways you can
        manipulate the list.

    .. automethod:: __iter__
    .. automethod:: __len__
    .. automethod:: __getitem__


    :class:`FieldList` is not limited to enclosing simple fields; and can
    indeed represent a list of enclosed forms by combining FieldList with
    FormField::

        class IMForm(Form):
            protocol = SelectField(choices=[('aim', 'AIM'), ('msn', 'MSN')])
            username = StringField()

        class ContactForm(Form):
            first_name  = StringField()
            last_name   = StringField()
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
                return ', '.join(self.data)
            else:
                return ''

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
        def __init__(self, label=None, validators=None, remove_duplicates=True, **kwargs):
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


Additional Helper Classes
-------------------------

.. autoclass:: Flags

    Usage:

    .. code-block:: pycon

        >>> flags = Flags()
        >>> flags.required = True
        >>> 'required' in flags
        True
        >>> flags.nonexistent
        >>> 'nonexistent' in flags
        False


.. class:: Label

    On all fields, the `label` property is an instance of this class.
    Labels can be printed to yield a
    ``<label for="field_id">Label Text</label>``
    HTML tag enclosure. Similar to fields, you can also call the label with
    additional html params.

    .. attribute:: field_id

        The ID of the field which this label will reference.

    .. attribute:: text

        The original label text passed to the field's constructor.
