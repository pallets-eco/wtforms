Crash Course
============

So you’ve cracked your knuckles and started working on that awesome python
webapp you want to write. You get through writing a few pages and finally you
need to tackle that loathsome task: form input handling and validation. Enter
WTForms.

But why do I need *yet another* framework? Well, some webapp frameworks take
the approach of associating database models with form handling. While this can
be handy for very basic create/update views, chances are not every form you
need can map directly to a database model. Or maybe you already use a generic
form handling framework but you want to customize the HTML generation of those
form fields, and define your own validation.

With WTForms, your form field HTML can be generated for you, but we let you
customize it in your templates. This allows you to maintain separation of code
and presentation, and keep those messy parameters out of your python code.
Because we strive for loose coupling, you should be able to do that in any
templating engine you like, as well.


.. _download-installation:

Download / Installation
-----------------------

The easiest way to install WTForms is by using easy_install or pip:

.. code-block:: ruby

    easy_install WTForms
    pip install WTForms

You can also `download`_ WTForms manually
from PyPI and then run ``python setup.py install``.

If you're the sort that likes to risk it all and run the latest version from
Mercurial, you can grab a `packaged up version`_
of the tip, or head over to `Bitbucket`_ 
and clone the repository.

.. _download: http://pypi.python.org/pypi/WTForms 
.. _packaged up version: http://bitbucket.org/simplecodes/wtforms/get/tip.zip
.. _Bitbucket: http://bitbucket.org/simplecodes/wtforms


Key Concepts
------------

 - **Forms** are the core container of WTForms. Forms represent a collection of
   fields, which can be accessed on the form dictionary-style or atrribute
   style.
 - **Fields** do most of the heavy lifting. Each field represents a *data type*
   and the field handles coercing form input to that datatype. For example,
   `IntegerField` and `TextField` represent two different data types. Fields
   contain a number of useful properties, such as a label, description, and a
   list of validation errors, in addition to the data the field contains.
 - Every field has a **Widget** instance. The widget's job is rendering an HTML
   representation of that field. Widget instances can be specified for each
   field but every field has one by default which makes sense. Some fields are
   simply conveniences, for example `TextAreaField` is simply a `TextField`
   with the default widget being a `TextArea`.
 - In order to specify validation rules, fields contain a list of **Validators**.

Getting Started
---------------

Let's get right down to business and define our first form::

    from wtforms import Form, BooleanField, TextField, validators

    class RegistrationForm(Form):
        username     = TextField('Username', [validators.Length(min=4, max=25)])
        email        = TextField('Email Address', [validators.Length(min=6, max=35)])
        accept_rules = BooleanField('I accept the site rules', [validators.Required()])

When you create a form, you define the fields in a way that is similar to the
way many ORM’s have you define their columns; By defining class variables which
are instantiations of the fields.

Because forms are regular Python classes, you can easily extend them as you
would expect::

    class ProfileForm(Form):
        birthday  = DateTimeField('Your Birthday', format='%m/%d/%y')
        signature = TextAreaField('Forum Signature')

    class AdminProfileForm(ProfileForm):
        username = TextField('Username', [validators.Length(max=40)])
        level    = IntegerField('User Level', [validators.NumberRange(min=0, max=10)])

Via subclassing, `AdminProfileForm`, gains all the fields already defined in
`ProfileForm`. This allows you to easily share common subsets of fields between
forms, such as the example above, where we are adding admin-only fields to
`ProfileForm`.


Using Forms
~~~~~~~~~~~

Using a form is as simple as instantiating it. Consider the following
django-like view, using the `RegistrationForm` we defined earlier::

    def register(request):
        form = RegistrationForm(request.POST)
        if request.method == 'POST' and form.validate():
            user = User()
            user.username = form.username.data
            user.email = form.email.data
            user.save()
            redirect('register')
        return render_response('register.html', form=form)

First, we instantiate the form, providing it with any data available in
``request.POST``. We then check if the request is made using POST, and if it is, 
we validate the form, and check that the user accepted the rules. If successful, 
we create a new User and assign the data from the validated form to it, and save
it.


Editing existing objects
^^^^^^^^^^^^^^^^^^^^^^^^

Our earlier registration example showed how to accept input and validate it for
new entries, but what if we want to edit an existing object? Easy::

    def edit_profile(request):
        user = request.current_user
        form = ProfileForm(request.POST, user)
        if request.method == 'POST' and form.validate():
            form.populate_obj(user)
            user.save()
            redirect('edit_profile')
        return render_response('edit_profile.html', form=form)

Here, we instantiate the form by providing both request.POST and the user object
to the form. By doing this, the form will get any data that isn't present in the 
post data from the `user` object.

We're also using the form's `populate_obj` method to re-populate the user
object with the contents of the validated form. This method is provided for
convenience, for use when the field names match the names on the object you're
providing with data. Typically, you will want to assign the values manually, but
for this simple case it's perfect. It can also be useful for CRUD and admin
forms.


Exploring in the console
^^^^^^^^^^^^^^^^^^^^^^^^

WTForms forms are very simple container objects, and perhaps the easiest way to
find out what's available to you in a form is to play around with a form in the
console::

    >>> from wtforms import Form, TextField, validators
    >>> class UsernameForm(Form):
    ...     username = TextField('Username', [validators.Length(min=5)], default=u'test')
    ...
    >>> form = UsernameForm()
    >>> form['username']
    <wtforms.fields.TextField object at 0x827eccc>
    >>> form.username.data
    u'test'
    >>> form.validate()
    False
    >>> form.errors
    {'username': [u'Field must be at least 5 characters long.']}

What we've found here is that when you instantiate a form, it contains
instances of all the fields, which can be accessed via either dictionary-style
or attribute-style. These fields have their own properties, as does the enclosing form.

When we validate the form, it returns False, meaning at least one validator was
not satisfied. form.errors will give you a summary of all the errors.

.. code-block:: python

    >>> form2 = UsernameForm(username=u'Robert')
    >>> form2.data
    {'username': u'Robert'}
    >>> form2.validate()
    True

This time, we passed a new value for username when instantiating UserForm, and
it was sufficient to validate the form.


How Forms get data
~~~~~~~~~~~~~~~~~~

In addition to providing data using the first two arguments (`formdata` and
`obj`), you can pass keyword arguments to populate the form. Note though that a
few names are reserved: `formdata`, `obj`, and `prefix`.

`formdata` takes precendence over `obj`, which itself takes precedence over
keyword arguments. For example::

    def change_username(request):
        user = request.current_user
        form = ChangeUsernameForm(request.POST, user, username='silly')
        if request.method == 'POST' and form.validate():
            user.username = form.username.data
            user.save()
            return redirect('change_username')
        return render_response('change_username.html', form=form)

While you almost never use all three methods together in practice, it
illustrates how WTForms looks up the `username` field:

1. Check if `request.POST` has a `username` key.
2. Check if `user` has an attribute named `username`.
3. Check if a keyword argument named `username` was provided.
4. Finally, if everything else fails, use the default value provided by the
   field, if any.


Validators
~~~~~~~~~~

Validation in WTForms is done by providing a field with a set of validators to
run when the containing form is validated. You provide these via the field
constructor's second argument, `validators`::

    class ChangeEmailForm(Form):
        email = TextField('Email', [validators.Length(min=6, max=120), validators.Email()])

You can provide any number of validators to a field. Typically, you will want to
provide a custom error message::

    class ChangeEmailForm(Form):
        email = TextField('Email', [
            validators.Length(min=6, message=_(u'Little short for an email address?')),
            validators.Email(message=_(u'That\'s not a valid email address.'))
        ])

It is generally preferable to provide your own messages, as the default messages
by necessity are generic. This is also the way to provide localised error
messages.

For a list of all the built-in validators, check the :mod:`Validators Reference <wtforms.validators>`


Rendering Fields
~~~~~~~~~~~~~~~~

Rendering a field is as simple as coercing it to a string::

    >>> from wtforms import Form, TextField
    >>> class SimpleForm(Form):
    ...   content = TextField('content')
    ...
    >>> form = SimpleForm(content='foobar')
    >>> str(form.content)
    '<input id="content" name="content" type="text" value="foobar" />'
    >>> unicode(form.content)
    u'<input id="content" name="content" type="text" value="foobar" />'

However, the real power comes from rendering the field with its :meth:`~wtforms.fields.Field.__call__`
method. By calling the field, you can provide keyword arguments, which will be
injected as html parameters in the output::

    >>> form.content(style="width: 200px;", class_="bar")
    u'<input class="bar" id="content" name="content" style="width: 200px;" type="text" value="foobar" />'

Now let's apply this power to rendering a form in a `Jinja <http://jinja.pocoo.org/>`_
template. First, our form::

    class LoginForm(Form):
        username = TextField('Username')
        password = PasswordField('Password')

    form = LoginForm()

And the template:

.. code-block:: html+jinja

    <form method="POST" action="/login">
        <div>{{ form.username.label }}: {{ form.username(class="css_class") }}</div>
        <div>{{ form.password.label }}: {{ form.password() }}</div>
    </form>

Alternately, if you're using Django templates, you can use the `form_field`
templatetag we provide in our Django extension, when you want to pass keyword
arguments:

.. code-block:: html+django

    {% load wtforms %}
    <form method="POST" action="/login">
        <div>
            {{ form.username.label }}:
            {% form_field form.username class="css_class" %}
        </div>
        <div>
            {{ form.password.label }}:
            {{ form.password }}
        </div>
    </form>

Both of these will output:

.. code-block:: html

    <form method="POST" action="/login">
        <div>
            <label for="username">Username</label>:
            <input class="css_class" id="username" name="username" type="text" value="" />
        </div>
        <div>
            <label for="password">Password</label>:
            <input id="password" name="password" type="password" value="" />
        </div>
    </form>

WTForms is template engine agnostic, and will work with anything that allows
attribute access, string coercion, and/or function calls. The `form_field`
templatetag is provided as a convenience as you can't pass arguments in Django
templates.


Displaying Errors
~~~~~~~~~~~~~~~~~

Now that we have a template for our form, let's add error messages:

.. code-block:: html+jinja

    <form method="POST" action="/login">
        <div>{{ form.username.label }}: {{ form.username(class="css_class") }}</div>
        {% if form.username.errors %}
            <ul class="errors">{% for error in form.username.errors %}<li>{{ error }}</li>{% endfor %}</ul>
        {% endif %}

        <div>{{ form.password.label }}: {{ form.password() }}</div>
        {% if form.password.errors %}
            <ul class="errors">{% for error in form.password.errors %}<li>{{ error }}</li>{% endfor %}</ul>
        {% endif %}
    </form>

If you prefer one big list of errors at the top, this is also easy:

.. code-block:: html+jinja

    {% if form.errors %}
        <ul class="errors">
            {% for field_name, field_errors in form.errors if field_errors %}
                {% for error in field_errors %}
                    <li>{{ form[field_name].label }}: {{ error }}</li>
                {% endfor %}
            {% endfor %}
        </ul>
    {% endif %}

As error handling can become a rather verbose affair, it is preferable to use
Jinja macros (or equivalent) to reduce boilerplate in your templates.
(:ref:`example <jinja-macros-example>`)

Custom Validators
~~~~~~~~~~~~~~~~~

There are two ways to provide custom validators. By defining a custom validator
and using it on a field::

    from wtforms.validators import ValidationError

    def is_42(form, field):
        if field.data != 42:
            raise ValidationError('Must be 42')

    class FourtyTwoForm(Form):
        num = IntegerField('Number', [is_42])

Or by providing an in-form field-specific validator::

    class FourtyTwoForm(Form):
        num = IntegerField('Number')

        def validate_num(form, field):
            if field.data != 42:
                raise ValidationError(u'Must be 42')

For more complex validators that take parameters, check the :ref:`custom-validators` section. 

