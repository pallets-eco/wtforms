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
        accept_rules = BooleanField('I accept the site rules', [validators.Required('You must accept to continue.')])

The `RegistrationForm` class can be defined in any python file in your project.
Some people put their forms alongside the associated views in their `views.py`,
while others prefer to create a `forms.py` to place their form defintions.

Now that the form definition is out of the way, let's write our register view::

    def register(request):
        form = RegistrationForm(request.POST)
        if request.POST and form.validate():
            user = User(form.email.data, form.password.data)
            # save new user here
            return render_response('confirmation.html', user=user)
        return render_response('register.html', form=form)

In the register view, we instantiate the form and pass it any received post
data. The form will pass this along to all its fields, who will pick up any
data they care about, converting it as needed.  This converted data is
available, naturally, on the `data` property of the field.

Now that we've got the view, all we need to do is write a template:

.. code-block:: html+jinja

    <form method="post" action="/register">
    <table>
      <tr>
        <th>{{ form.email.label }}</th>
        <td>{{ form.email(class="big_text") }}</td>
      </tr>
      <tr>
        <th>{{ form.password.label }}</th>
        <td>{{ form.password(class="big_text") }}</td>
      </tr>
      <tr>
        <td></td>
        <td>{{ form.accept_rules }} {{ form.accept_rules.label }}</td>
    </table>
    <input type="submit" value="Register!" />
    </form>

We pass the entire form into the template so that we can access its rendering
helpers. Under the hood, rendering is done by the widget associated with a
field. Simply printing a form field will call its widget with an empty argument
list, and calling the field passes keyword arguments along. You'll notice that
we use the field's `label` property which is another printable object that
generates an HTML ``<label for=`` associated with the field.

Populating model objects automatically: comment posting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When your form has more than a few fields, it becomes a bit unwieldy then to
have to refer to each field's `data` property individually. Instead of
explicitly moving data over, WTForms can be told to populate your model object
automatically. This is done using the :meth:`~wtforms.form.Form.auto_populate`
method:: 

    from wtforms import Form, HiddenField, TextField, TextAreaField
    from wtforms import validators as v
    import re
    
    def strip_html(data):
        return re.sub(r'<.*?>', '', data)

    class CommentForm(Form):
        name     = TextField('Your Name', [v.Required()]) 
        email    = TextField('Email', [v.Optional(), v.Email()])
        message  = TextAreaField('Comment', [v.Required()], filters=[strip_html])
        # and so on

    def post_comment(request, article_id):
        form = CommentForm(request.POST)
        if request.POST and form.validate():
            comment = Comment(article_id=article_id)
            form.auto_populate(comment)
            # save comment here
            return redirect('/article/%d' % article_id)
        return render_response('post_comment.html', form=form)

What :meth:`~wtforms.form.Form.auto_populate` does is copy the data from each
field onto attributes of the same name on your model object.  This can be
potentially dangerous, so use with care to only define properties you mean, and
to validate your input. 

In addition, the example uses a simple filter to strip HTML tags out of the
input. Filters can be any one-argument callable, so you can
pass library functions and lambdas as needed.
        
Advanced forms with dynamic select fields and form enclosures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the administration part of your blog, you'll want a way to write articles

::
    from wtforms import Form, DateTimeField, FormField, SelectField, TextField, TextAreaField
    from wtforms import validators as v

    class ArticleContentForm(Form):
        d
    
    class ArticleForm(Form):
        title       = TextField(u'Title)
        category_id = SelectField(u'Category')
        posted      = DateTimeField(u'Posted date')
        summary     = TextAreaField(u'Summary')
        content     = FormField(ArticleContentForm)

TODO: composed forms using ListField/FormField,
explain validators and widgets and how to switch them around, and neat
rendering things.

TODO: At end, provide links to other parts of documentation as needed.

