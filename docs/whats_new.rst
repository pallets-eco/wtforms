What's New in WTForms 3
=======================

New Features
------------

WTForms 3 is something something TODO


Past Major Releases
-------------------

WTForms 2
~~~~~~~~~

WTForms 2 was the first major version bump since WTForms 1.0. Coming with it
are a number of major changes that allow far more customization of core
WTForms features. This is done to make WTForms even more capable when working
along with companion libraries.


New Features
^^^^^^^^^^^^

* :doc:`Class Meta <meta>` paradigm allows customization of many aspects of WTForms.
* :doc:`CSRF <csrf>` and :doc:`i18n <i18n>` are core features not needing
  extensions anymore.
* Widget rendering changes:

  * Passing ``<attribute name>=False`` to WTForms widget rendering is now
    ignored, making it easier to deal with boolean HTML attributes.
  * Creating an html attribute ``data-foo`` can be done by passing the keyword
    ``data_foo`` to the widget.


Deprecated API's
^^^^^^^^^^^^^^^^

These API's still work, but in most cases will cause a DeprecationWarning.
The deprecated API's will be removed in WTForms 3.0, so write code against
the new API's unless it needs to work across both WTForms 1.x and 2.x

* **Core**

  * :meth:`Form._get_translations <wtforms.form.Form._get_translations>` Use
    :meth:`Meta.get_translations <wtforms.meta.DefaultMeta.get_translations>`
    instead.
  * The ``TextField`` alias for
    :class:`~wtforms.fields.StringField` is deprecated.
  * ``wtforms.validators.Required`` is now
    :class:`wtforms.validators.DataRequired`
  * ``wtforms.fields._unset_value`` is now ``wtforms.utils.unset_value``


* **WTForms Extensions**
  All the extensions are being deprecated. We feel like the extensions we had
  would actually benefit from being pulled outside the WTForms package,
  because it would allow them to have a separate release schedule that suits
  their companion libraries.

  * ``wtforms.ext.appengine`` Is deprecated, see `WTForms-Appengine`_
  * ``wtforms.ext.csrf`` CSRF protection is now :doc:`built in <csrf>`
  * ``wtforms.ext.dateutil`` Is deprecated, but does not have a new home yet.
  * ``wtforms.ext.django`` Is deprecated. See `WTForms-Django`_
  * ``wtforms.ext.i18n`` i18n is now :doc:`built in <i18n>`
  * ``wtforms.ext.sqlalchemy`` Is deprecated, look at `WTForms-Alchemy`_
    (`docs <WTForms-Alchemy-docs_>`_)

.. _WTForms-Alchemy: https://pypi.org/project/WTForms-Alchemy/
.. _WTForms-Alchemy-docs: https://wtforms-alchemy.readthedocs.io/
.. _WTForms-Appengine: https://github.com/wtforms/wtforms-appengine
.. _WTForms-Django: https://github.com/wtforms/wtforms-django


Low-level Changes
^^^^^^^^^^^^^^^^^

Most of these changes shouldn't affect the typical library user, however we
are including these changes for completeness for those who are creating
companion libraries to WTForms.

* ``BaseForm._fields`` is now an OrderedDict, not a plain dict.

* :class:`~wtforms.form.FormMeta` now manages an attribute called
  ``_wtforms_meta`` which is a subclass of any ``class Meta`` defined on
  ancestor form classes.

* A new keyword-param called simply ``data=`` to the Form constructor has been
  added and positioned as the place where soon we will be able to accept
  structured data which is neither formdata, object data, or defaults.
  Currently this parameter is merged with the kwargs, but the intention is to
  handle other structured data (think JSON).

* :attr:`Filters <wtforms.fields.Field.filters>` on fields stop on the first
  ValueError, instead of continuing on to the next one.
