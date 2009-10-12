.. _extensions:

Extensions
==========
.. module:: wtforms.ext

WTForms ships with a number of extensions that make it easier to work with
other frameworks and libraries, such as Django.

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

.. autofunction:: model_form(model, base_class=Form, include_pk=False)

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
using django ORM data can be quite repetetive. To this end, we have added some
helpful tools to use the django ORM along with wtforms


.. autoclass:: QuerySetSelectField(default field args, queryset=None, label_attr='', allow_blank=False, blank_text=u'')

    .. code-block:: python

        class ArticleEdit(Form):
            title    = TextField()
            column   = QuerySetSelectField(label_attr='title', allow_blank=True)
            category = QuerySetSelectField(queryset=Category.objects.all())

        def edit_article(request, id):
            article = Article.objects.get(pk=id)
            form = ArticleEdit(obj=article)
            form.column.queryset = Column.objects.filter(author=request.user)

    As shown in the above example, the queryset can be set dynamically in the
    view if needed instead of at form construction time, allowing the select
    field to consist of choices only relevant to the user.

.. autoclass:: ModelSelectField(default field args, model=None, label_attr='', allow_blank=False, blank_text=u'')


SQLAlchemy
----------
.. module:: wtforms.ext.sqlalchemy

This extension provides SelectField integration with SQLAlchemy ORM models,
similar to those in the Django extension.


ORM-backed fields
~~~~~~~~~~~~~~~~~
.. module:: wtforms.ext.sqlalchemy.fields

These fields are provided to make it easier to use data from ORM objects in
your forms. Due to the complication of dealing with multiple-primary-keyed
tables, currently it is only possible to use these fields with simple integer
primary keyed ORM models.

.. code-block:: python

    def enabled_categories():
        return Category.query.filter_by(enabled=True)

    class BlogPostEdit(Form):
        title    = TextField()
        blog     = QuerySelectField()
        category = QuerySelectField(query_factory=enabled_categories, allow_blank=True)

    def edit_blog_post(request, id):
        post = Post.query.get(id)
        form = ArticleEdit(obj=post)
        form.blog.query = Blog.query.filter(Blog.author == request.user).order_by(Blog.name)


.. autoclass:: QuerySelectField(default field args, query_factory=None, pk_attr='id', label_attr='', allow_blank=False, blank_text=u'')

.. autoclass:: ModelSelectField(default field args, model=None, pk_attr='id', label_attr='', allow_blank=False, blank_text=u'')

