.. _extensions:

Extensions
==========
.. module:: wtforms.ext

WTForms ships with a number of extensions that make it easier to work with
other frameworks and libraries, such as Django.

Appengine
---------
.. module:: wtforms.ext.appengine

WTForms now includes support for AppEngine fields as well as auto-form
generation.

Model Forms
~~~~~~~~~~~
.. module:: wtforms.ext.appengine.db

See the module docstring for examples on how to use :func:`model_form`.

.. autofunction:: model_form(model, base_class=Form, only=None, exclude=None, field_args=None, converter=None)

Datastore-backed Fields
~~~~~~~~~~~~~~~~~~~~~~~
.. module:: wtforms.ext.appengine.fields

.. autoclass:: ReferencePropertyField(default field arguments, reference_class=None, get_label=None, allow_blank=False, blank_text=u'')

.. autoclass:: StringListPropertyField(default field arguments)

.. autoclass:: GeoPtPropertyField(default field arguments)

Dateutil
--------
.. module:: wtforms.ext.dateutil.fields

For better date-time parsing using the `python-dateutil`_  package,
:mod:`wtforms.ext.dateutil` provides a set of fields to use to accept a wider
range of date input. 

.. _python-dateutil: http://labix.org/python-dateutil

.. autoclass:: DateTimeField(default field arguments, parse_kwargs=None, display_format='%Y-%m-%d %H:%M')

.. autoclass:: DateField(default field arguments, parse_kwargs=None, display_format='%Y-%m-%d')

Django
------
.. module:: wtforms.ext.django

This extension provides templatetags to make it easier to work with Django
templates and WTForms' html attribute rendering. It also provides a generator
for automatically creating forms based on Django ORM models.

Templatetags
~~~~~~~~~~~~
.. module:: wtforms.ext.django.templatetags.wtforms

Django templates does not allow arbitrarily calling functions with parameters,
making it impossible to use the html attribute rendering feature of WTForms. To
alleviate this, we provide a templatetag.

Adding :mod:`wtforms.ext.django` to your INSTALLED_APPS will make the wtforms 
template library available to your application.  With this you can pass extra 
attributes to form fields similar to the usage in jinja:

.. code-block:: django

    {% load wtforms %}

    {% form_field form.username class="big_text" onclick="do_something()" %}

**Note** By default, using the `{{ form.field }}` syntax in django models will
be auto-escaped.  To avoid this happening, use Django's `{% autoescape off %}`
block tag or use WTForms' `form_field` template tag.

Model forms
~~~~~~~~~~~
.. module:: wtforms.ext.django.orm

.. autofunction:: model_form(model, base_class=Form, only=None, exclude=None, field_args=None, converter=None)

    :func:`model_form` attempts to glean as much metadata as possible from
    inspecting the model's fields, and will even attempt to guess at what
    validation might be wanted based on the field type. For example, converting
    an `EmailField` will result in a :class:`~wtforms.fields.TextField` with
    the :func:`~wtforms.validators.email` validator on it. if the `blank`
    property is set on a model field, the resulting form field will have the
    :func:`~wtforms.validators.optional` validator set.

    Just like any other Form, forms created by ModelForm can be extended via
    inheritance::

        UserFormBase = model_form(User)

        class UserForm(UserFormBase):
            new_pass     = PasswordField('', [validators.optional(), validators.equal_to('confirm_pass')])
            confirm_pass = PasswordField()

    When combined with :meth:`form iteration <wtforms.form.Form.__iter__>`,
    model_form is a handy way to generate dynamic CRUD forms which update with
    added fields to the model. One must be careful though, as it's possible the
    generated form fields won't be as strict with validation as a hand-written
    form might be.

ORM-backed fields
~~~~~~~~~~~~~~~~~
.. module:: wtforms.ext.django.fields


While linking data to most fields is fairly easy, making drop-down select lists
using django ORM data can be quite repetitive. To this end, we have added some
helpful tools to use the django ORM along with wtforms.


.. autoclass:: QuerySetSelectField(default field args, queryset=None, get_label=None, allow_blank=False, blank_text=u'')

    .. code-block:: python

        class ArticleEdit(Form):
            title    = TextField()
            column   = QuerySetSelectField(get_label='title', allow_blank=True)
            category = QuerySetSelectField(queryset=Category.objects.all())

        def edit_article(request, id):
            article = Article.objects.get(pk=id)
            form = ArticleEdit(obj=article)
            form.column.queryset = Column.objects.filter(author=request.user)

    As shown in the above example, the queryset can be set dynamically in the
    view if needed instead of at form construction time, allowing the select
    field to consist of choices only relevant to the user.

.. autoclass:: ModelSelectField(default field args, model=None, get_label='', allow_blank=False, blank_text=u'')


SQLAlchemy
----------
.. module:: wtforms.ext.sqlalchemy

This extension provides SelectField integration with SQLAlchemy ORM models,
similar to those in the Django extension.


ORM-backed fields
~~~~~~~~~~~~~~~~~
.. module:: wtforms.ext.sqlalchemy.fields

These fields are provided to make it easier to use data from ORM objects in
your forms.

.. code-block:: python

    def enabled_categories():
        return Category.query.filter_by(enabled=True)

    class BlogPostEdit(Form):
        title    = TextField()
        blog     = QuerySelectField(get_label='title')
        category = QuerySelectField(query_factory=enabled_categories, allow_blank=True)

    def edit_blog_post(request, id):
        post = Post.query.get(id)
        form = ArticleEdit(obj=post)
        # Since we didn't provide a query_factory for the 'blog' field, we need
        # to set a dynamic one in the view.
        form.blog.query = Blog.query.filter(Blog.author == request.user).order_by(Blog.name)


.. autoclass:: QuerySelectField(default field args, query_factory=None, get_pk=None, get_label=None, allow_blank=False, blank_text=u'')

.. autoclass:: QuerySelectMultipleField(default field args, query_factory=None, get_pk=None, get_label=None, allow_blank=False, blank_text=u'')


CSRF
----
.. module:: wtforms.ext.csrf

The CSRF package includes tools that help you implement checking against
cross-site request forgery ("csrf"). Due to the large number of variations on
approaches people take to CSRF (and the fact that many make compromises) the
base implementation allows you to plug in a number of CSRF validation
approaches.

CSRF implementations are made by subclassing
:class:`~wtforms.ext.csrf.form.SecureForm`. For utility, we have provided one
possible CSRF implementation in the package that can be used with many
frameworks for session-based hash secure keying,
:class:`~wtforms.ext.csrf.session.SessionSecureForm`.

All CSRF implementations hinge around creating a special token, which is put in
a hidden field on the form named 'csrf_token', which must be rendered in your
template to be passed from the browser back to your view. There are many
different methods of generating this token, but they are usually the result of
a cryptographic hash function against some data which would be hard to forge.

.. module:: wtforms.ext.csrf.form

.. autoclass:: SecureForm

    .. automethod:: generate_csrf_token

    .. automethod:: validate_csrf_token

Creating your own CSRF implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here we will sketch out a simple theoretical CSRF implementation which
generates a hash token based on the user's IP.

**Note** This is a simplistic example meant to illustrate creating a CSRF
implementation. This isn't recommended to be used in production because the
token is deterministic and non-changing per-IP, which means this isn't the
most secure implementation of CSRF.

First, let's create our SecureForm base class::

    from wtforms.ext.csrf import SecureForm
    from hashlib import md5

    SECRET_KEY = '1234567890'

    class IPSecureForm(SecureForm):
        """
        Generate a CSRF token based on the user's IP. I am probably not very
        secure, so don't use me.
        """

        def generate_csrf_token(self, csrf_context):
            # csrf_context is passed transparently from the form constructor,
            # in this case it's the IP address of the user
            token = md5(SECRET_KEY + csrf_context).hexdigest()
            return token

        def validate_csrf_token(self, field):
            if field.data != field.current_token:
                raise ValueError('Invalid CSRF')


Now that we have this taken care of, let's write a simple form and view which would implement this::

    class RegistrationForm(IPSecureForm):
        name = TextField('Your Name')
        email = TextField('Email', [validators.email()])

    def register(request):
        form = RegistrationForm(request.POST, csrf_context=request.ip)

        if request.method == 'POST' and form.validate():
            pass # We're all good, create a user or whatever it is you do
        elif form.csrf_token.errors:
            pass # If we're here we suspect the user of cross-site request forgery
        else:
            pass # Any other errors

        return render('register.html', form=form)

And finally, a simple template:

.. code-block:: html+jinja

    <form action="register" method="POST">
        {{ form.csrf_token }}
        <p>{{ form.name.label }}: {{ form.name }}</p>
        <p>{{ form.email.label }}: {{ form.email }}</p>
        <input type="submit" value="Register">
    </form>


Please note that implementing CSRF detection is not fool-proof, and even with
the best CSRF protection implementation, it's possible for requests to be
forged by expert attackers. However, a good CSRF protection would make it
infeasible for someone from an external site to hijack a form submission from
another user and perform actions as them without additional a priori knowledge.

In addition, it's important to understand that very often, the more strict the
CSRF protection, the higher the chance of false positives occurring (ie,
legitimate users getting blocked by your CSRF protection) and choosing a CSRF
implementation is actually a matter of compromise. We will attempt to provide a
handful of usable reference algorithms built in to this library in the future, to
allow that choice to be easy.

Some tips on criteria people often examine when evaluating CSRF implementations:

 * **Reproducability** If a token is based on attributes about the user, it
   gains the advantage that one does not need secondary storage in which to
   store the value between requests. However, if the same attributes can be
   reproduced by an attacker, then the attacker can potentially forge this
   information.

 * **Reusability**. It might be desired to make a completely different token
   every use, and disallow users from re-using past tokens. This is an
   extremely powerful protection, but can have consequences on if the user uses
   the back button (or in some cases runs forms simultaneously in multiple
   browser tabs) and submits an old token, or otherwise. A possible compromise
   is to allow reusability in a time window (more on that later).

 * **Time Ranges** Many CSRF approaches use time-based expiry to make sure that
   a token cannot be (re)used beyond a certain point. Care must be taken in
   choosing the time criteria for this to not lock out legitimate users. For
   example, if a user might walk away while filling out a long-ish form, or to
   go look for their credit card, the time for expiry should take that into
   consideration to provide a balance between security and limiting user
   inconvenience.

 * **Requirements** Some CSRF-prevention methods require the use of browser
   cookies, and some even require client-side scripting support. The webmaster
   implementing the CSRF needs to consider that such requirements (though
   effective) may lock certain legitimate users out, and make this
   determination whether it is a good idea to use. For example, for a site
   already using cookies for login, adding another for CSRF isn't as big of a
   deal, but for other sites it may not be feasible.


Session-based CSRF implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: wtforms.ext.csrf.session

**Usage**

First, create a SessionSecureForm subclass that you can use as your base class
for any forms you want CSRF support for::

    from wtforms.ext.csrf.session import SessionSecureForm

    class MyBaseForm(SessionSecureForm):
        SECRET_KEY = 'EPj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Ym'
        TIME_LIMIT = timedelta(minutes=20)

Now incorporate it into any form/view by further subclassing::

    class Registration(MyBaseForm):
        name = TextField()

    def view(request):
        form = Registration(request.POST, csrf_context=request.session)
        # rest of view here

Note that request.session is passed as the ``csrf_context=`` parameter, this is
so that the CSRF token can be stored in your session for comparison on a later
request.

.. autoclass:: SessionSecureForm

    A provided CSRF implementation which puts CSRF data in a session. Must be
    subclassed to be used.
    
    **Class Attributes**
    .. attribute:: SECRET_KEY
        
        Must be set by subclasses to a random byte string that will be used to generate HMAC digests. 

    .. attribute:: TIME_LIMIT

        If None, CSRF tokens never expire. If set to a ``datetime.timedelta``,
        this is how long til a generated token expires. Defaults to
        ``timedelta(minutes=30)``

