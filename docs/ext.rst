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
.. module:: wtforms.ext.django.templatetags

Django templates does not allow arbitrarily calling functions with parameters,
making it impossible to use the html attribute rendering feature of WTForms. To
alleviate this, we provide a templatetag.

Adding :mod:`wtforms.ext.django` to your INSTALLED_APPS will make the wtforms 
template library available to your application.  With this you can pass extra 
attributes to form fields similar to the usage in jinja:

.. code-block:: django

  {% load wtforms %}

    {% form_field form.username class="big_text" onclick="do_something()" %}

**Note** if you're using the newest development version of Django, output from 
wtforms using the `{{ form.field }}` syntax will be auto-escaped.  
To avoid this happening, use the Django's `{% autoescape off %}` block tag or 
use WTForms' `form_field` template tag.

Model forms
~~~~~~~~~~~
.. module:: wtforms.ext.django.models

Similar to the ModelForm available in Django's newforms, wtforms can generate
forms from your Django models.  To do this, use the
:func:`wtforms.ext.django.models.model_form` function::

    from wtforms.ext.django import model_form
    from myproject.myapp.models import User

    UserForm = model_form(User)

You can even extend UserForm and add additional fields as you need.
