FAQ
===

This contains the most commonly asked questions about WTForms. The most current
version of this document can always be found on the `WTForms Website`_.

.. _WTForms Website: http://wtforms.simplecodes.com

Why does WTForms copy Django Forms?
-----------------------------------

Were we a bit more audacious, we'd probably say Django Forms copied us, but the
reality is that WTForms and Django's "newforms" were actually written at about
the same time.

When WTForms was written, our primary goals were to provide HTML customization
through templates, easily customized validation and a simple, declarative
ORM-style API. At the time there was no newforms and the other alternatives
either didn't support HTML generation, were very tightly coupled with a
single framework, or relied too heavily on an ORM.


Does WTForms work with [library here]?
--------------------------------------

The answer is most likely **yes**. WTForms tries to provide as usable an API as
possible. We've listed here some of the known libraries to work with WTForms,
but if it's not listed, it doesn't mean it won't work.

* **Request/Form Input**

  * Django
  * Webob (Includes Pylons, Google App Engine, Turbogears)
  * Werkzeug
  * any other cgi.FieldStorage-type multidict

* **Templating Engines**

  * Jinja2
  * Mako
  * Django Templates (To get the full power of WTForms in your templates, you
    will need to use the Django :mod:`extension <wtforms.ext.django>`.)
  * Genshi (WTForms output will be auto-escaped by Genshi, you will need to
    mark it as safe)

* **Database Objects**

  * Pretty much any ORM or object-DB should work, as long as data objects allow
    attribute access to their members.

    Special support is there for SQLAlchemy, Google App Engine, and Django
    collections via :mod:`extensions <wtforms.ext>`.


Does WTForms support unicode?
-----------------------------

Simple answer: Yes.

Longer answer: WTForms uses unicode strings throughout the source code, and
assumes that form input has already been coerced to unicode by your framework
(Most frameworks already do this.) WTForms fields render to unicode strings by
default, and therefore as long as your templating engine can work with that,
you should have no unicode issues.


What versions of Python are supported?
--------------------------------------

WTForms supports Python versions 2.4 and up. Presently, Python 3.x is not
supported, as we are waiting for library support by the major frameworks. As
soon as we have something we can test/deploy on we will consider making the
provisions to support WTForms for Python 3.x.


How can I contribute to WTForms?
--------------------------------

WTForms is not that scary. Really. We try to keep it as succint and readable as
possible. If you feel like you have something to contribute to WTForms, let us
know on the `mailing list`_. For bugs and feature requests, you can file a
ticket on the `project page`_.

.. _mailing list: http://groups.google.com/group/wtforms
.. _project page: http://bitbucket.org/simplecodes/wtforms


How do I mark in a template when a field is required?
-----------------------------------------------------

Some validators (notably Required and Optional) set flags on the fields'
:attr:`~wtforms.fields.Field.flags` object. To use this in a template, you can
do something like:

.. code-block:: html+jinja

    {% for field in form %}
        {{ field }}
        {% if field.flags.required %}*{% endif %}{{ field.label }}
    {% endfor %}


Does WTForms handle file uploads?
---------------------------------

Currently, it does not. This is because WTForms strives to be
framework-agnostic, and every web framework handles file uploads somewhat
differently. WTForms has a :class:`~wtforms.fields.FileField` which will let
you render a file input widget, but the rest is up to you. An example use in a
django-ish framework::

    class MyForm(Form):
        image = FileField()

    def my_view(request):
        form = MyForm(request.POST)
        file_wrapper = request.FILES[form.image.name]
        # Do things with your file wrapper now

Using ``form.image.name`` is an easy way to know what input name was generated
for your file input, even if the form is prefixed.


How do I... [convoluted combination of libraries]
-------------------------------------------------

You'll probably want to check out our 
:ref:`Solving Specific Problems <specific_problems>` doc.
