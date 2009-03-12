.. _tutorial:

Tutorial
========

This tutorial will step the user through the workings of a small web
application that makes use of WTForms.

WTForms is a library that provides form processing and rendering for a number
of frameworks. Whether you're using Django, Pylons, AppEngine, Werkzeug, or
another python framework, WTForms should work for you. Also, WTForms will work
along with nearly any template framework, or even in the absence of one.

Because there are minor differences between various frameworks, it is often
difficult to write code examples that will work exactly the same on every
framework. Due to this, we have opted to write this guide tailored to users of
a Django-like framework with Jinja-like templates. We aim to make the examples
clear enough that users of any other framework will see how WTForms can be
applied to their own framework.

Key Concepts
------------

**Forms**:
    The Form is the basic unit in WTForms, and all interaction with the
    framework starts here. A form is in essence a collection of named fields,
    each of which represents a bit of data.

**Fields**:
    Fields are defined on each form and understand something about the data
    they contain. Some fields take user input and convert it to another data
    type, one more convenient for working with; such as integers or `datetime`
    objects.

**Validators**:
    A key part of what makes WTForms useful is the ability to validate data.
    Every field can have any number of validators. Validators are simple
    callables or classes that look at a field's data and will raise errors. When
    a form is validated, each of the fields on the form are validated, and any
    errors that are found are collected for later use or display.

**Widgets**:
    A tedious part of web development is writing the HTML or template logic to
    display input fields, especially those of create/edit forms. WTForms uses
    widgets to achieve that purpose. Widgets are simple classes that handle the
    difficult work of rendering the field's contents while allowing you to
    still customize displayed HTML if needed.  Every field contains a single
    widget.

**Filters**:
    Though not a commonly used feature, fields can contain any number of
    filters, which are simple functions that modify the input data. Filters
    can, for example, strip off extra whitespace, strip out HTML, or convert a
    string to uppercase.
    
The Uber-Blog
-------------

Your first application *is* a blog, right? Well if it's not, too bad, because
that's what we're going to be writing.  In the process of going through this
sample application, we will take you through simple forms such as those which
simply take in a few scalar values, then to forms which interact with DB-backed
data, and finally to more complicated composed forms.

Taking normal input: Registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We want to set up a way for people to register accounts on the blog so that
users can post with confidence nobody is impersonating them.  For the
registration page, we define a Form::

    from wtforms import Form, BooleanField, TextField, PasswordField, validators

    class RegistrationForm(Form):
        email        = TextField('Email Address', [validators.Length(min=4, max=35)])
        password     = PasswordField('Password', [validators.Length(min=6)])
        accept_rules = BooleanField('I accept the site rules', [validators.Required('You must accept to continue.'])

The `RegistrationForm` class can be defined in any python file in your project.
Some people put their forms alongside the associated views in their `views.py`,
while others prefer to create a `forms.py` to place their form defintions.

Now that the form definition is out of the way, let's write our register view::

    def register(request):
        form = RegistrationForm(request.POST)
        if request.POST and form.validate():
            user = User(form.email.data, form.password.data)
            # save new user here
            return render('confirmation.html', {'user': user})
        return render('register.html', {'form': form})

In the register view, we instantiate the form and pass it any received post
data. The form will pass this along to all its fields, who will pick up any
data they care about, converting it as needed.  This converted data is
available, naturally, on the `data` property of the field.


TODO: CRUD forms using auto_populate, composed forms using ListField/FormField,
explain validators and widgets and how to switch them around, and neat
rendering things.

TODO: At end, provide links to other parts of documentation as needed.

