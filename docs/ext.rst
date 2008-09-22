Extensions
==========

WTForms ships with a number of extensions that make it easier to work with
other frameworks and libraries, such as Django.

Django
------

This extension provides templatetags to make it easier to work with Django
templates and WTForms' html attribute rendering. It also provides a generator
for automatically creating forms based on Django ORM models.

Templatetags
~~~~~~~~~~~~

Django templates does not allow arbitrarily calling functions with parameters,
making it impossible to use the html attribute rendering feature of WTForms. To
alleviate this, we provide a templatetag.

(TODO)

Autogenerating forms based on models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(TODO)
