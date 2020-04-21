:orphan:

Extensions
==========

.. module:: wtforms.ext

.. warning::
    .. deprecated:: 2.0
        Everything in ``wtforms.ext`` is deprecated and will be removed
        in WTForms 3.0.

WTForms ships with a number of extensions that make it easier to work with
other frameworks and libraries, such as Django.


Appengine
---------

.. module:: wtforms.ext.appengine

.. warning::
    .. deprecated:: 2.0
        ``wtforms.ext.appengine`` is deprecated and will be removed in
        WTForms 3.0. Use `WTForms-Appengine`_ instead.

.. _WTForms-Appengine: https://github.com/wtforms/wtforms-appengine

WTForms includes support for AppEngine fields as well as auto-form
generation from models.


Model Forms
~~~~~~~~~~~

.. module:: wtforms.ext.appengine.db

See the module docstring for examples on how to use :func:`model_form`.

.. autofunction:: model_form(model, base_class=Form, only=None, exclude=None, field_args=None, converter=None)


Datastore-backed Fields
~~~~~~~~~~~~~~~~~~~~~~~

.. module:: wtforms.ext.appengine.fields

.. autoclass:: ReferencePropertyField(default field arguments, reference_class=None, get_label=None, allow_blank=False, blank_text='')

.. autoclass:: StringListPropertyField(default field arguments)

.. autoclass:: GeoPtPropertyField(default field arguments)


NDB
~~~

WTForms includes support for NDB models and can support mapping the
relationship fields as well as generating forms from models.

.. autoclass:: KeyPropertyField(default field arguments, reference_class=None, get_label=None, allow_blank=False, blank_text='')

.. module:: wtforms.ext.appengine.ndb

.. autofunction:: model_form(model, base_class=Form, only=None, exclude=None, field_args=None, converter=None)


Dateutil
--------

.. module:: wtforms.ext.dateutil
.. module:: wtforms.ext.dateutil.fields

.. warning::
    .. deprecated:: 2.0
        ``wtforms.ext.dateutil`` is deprecated and will be removed in
        WTForms 3.0.

For better date-time parsing using the `python-dateutil`_  package,
:mod:`wtforms.ext.dateutil` provides a set of fields to use to accept a wider
range of date input.

.. _python-dateutil: https://dateutil.readthedocs.io/

.. autoclass:: DateTimeField(default field arguments, parse_kwargs=None, display_format='%Y-%m-%d %H:%M')

.. autoclass:: DateField(default field arguments, parse_kwargs=None, display_format='%Y-%m-%d')


Django
------

.. module:: wtforms.ext.django

.. warning::
    .. deprecated:: 2.0
        ``wtforms.ext.django`` is deprecated and will be removed in
        WTForms 3.0. Use `WTForms-Django`_ instead.

.. _WTForms-Django: https://github.com/wtforms/wtforms-django

This extension provides templatetags to make it easier to work with Django
templates and WTForms' html attribute rendering. It also provides a generator
for automatically creating forms based on Django ORM models.


Templatetags
~~~~~~~~~~~~

.. module:: wtforms.ext.django.templatetags.wtforms

Django templates do not allow arbitrarily calling functions with parameters,
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
    an `EmailField` will result in a :class:`~wtforms.fields.StringField` with
    the :class:`~wtforms.validators.Email` validator on it. if the `blank`
    property is set on a model field, the resulting form field will have the
    :class:`~wtforms.validators.Optional` validator set.

    Just like any other Form, forms created by model_form can be extended via
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
            title    = StringField()
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

.. warning::
    .. deprecated:: 2.0
        ``wtforms.ext.sqlalchemy`` is deprecated and will be removed in
        WTForms 3.0. Use `WTForms-SQLAlchemy`_ instead.

.. _WTForms-SQLAlchemy: https://github.com/wtforms/wtforms-sqlalchemy

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
        title    = StringField()
        blog     = QuerySelectField(get_label='title')
        category = QuerySelectField(query_factory=enabled_categories, allow_blank=True)

    def edit_blog_post(request, id):
        post = Post.query.get(id)
        form = BlogPostEdit(obj=post)
        # Since we didn't provide a query_factory for the 'blog' field, we need
        # to set a dynamic one in the view.
        form.blog.query = Blog.query.filter(Blog.author == request.user).order_by(Blog.name)


.. autoclass:: QuerySelectField(default field args, query_factory=None, get_pk=None, get_label=None, allow_blank=False, blank_text=u'')

.. autoclass:: QuerySelectMultipleField(default field args, query_factory=None, get_pk=None, get_label=None)


Model forms
~~~~~~~~~~~

.. module:: wtforms.ext.sqlalchemy.orm

It is possible to generate forms from SQLAlchemy models similarly to how it can be done for Django ORM models.

.. autofunction:: model_form


CSRF
----

.. module:: wtforms.ext.csrf

.. warning::
    .. deprecated:: 2.0
        ``wtforms.ext.csrf`` is deprecated and will be removed in
        WTForms 3.0. CSRF protection is now built-in. See :doc:`csrf`.

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
        name = StringField()

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


I18n
----

.. module:: wtforms.ext.i18n

.. warning::
    .. deprecated:: 2.0
        ``wtforms.ext.i18n`` is deprecated and will be removed in
        WTForms 3.0. I18N support is now built-in. See :doc:`i18n`.

.. module:: wtforms.ext.i18n.form

.. autoclass:: Form
