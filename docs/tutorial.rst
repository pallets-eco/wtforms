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
a Django-like framework with Django-like templates. We aim to make the examples
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

Taking normal input: Login
~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to edit entries on your blog, you will need a login page to
authenticate you, so evil people cannot start posting in your stead. For our
login page, we will define a Form::

    from wtforms import Form, BooleanField, TextField, PasswordField, validators

    class LoginForm(Form):
        username    = TextField('Username', [validators.required()])
        password    = PasswordField('Password', [validators.length(max=50)])
        remember_me = BooleanField('Remember me')

The `LoginForm` class can be defined in any python file in your project.  Some
people put their forms alongside the associated views in their `views.py`,
while others prefer to create a `forms.py` to place their form defintions.

Now that the form definition is out of the way, let's write our login view::

    from django.contrib.auth import authenticate, login

    def login(request):
        form = LoginForm(request.POST)
        if request.POST and form.validate():
            user = authenticate(username=form.username.data, password=form.password.data)
            if user.is_active:
                login(request, user)
                response = HttpResponseRedirect('/blog_admin')
                if form.remember_me.data:
                    response.set_cookie('hash', user.get_hash())
                return response

        return render_to_response('login.html', {'form': form})

TODO: get a better example for the simple view.
