What's New in WTForms 2
=======================

WTForms 2 is the first major version bump since WTForms 1.0. Coming with it
are a number of major changes that allow far more customization of core 
WTForms features. This is done to make WTForms even more capable when working
along with companion libraries.


New Features
------------

TODO


Deprecated API's
----------------

Most API's work exactly the same as they did in WTForms 1.x, though some are 
deprecated and will cause a DeprecationWarning and will be removed in WTForms 3.

* **Form**

  * :meth:`Form._get_translations <wtforms.form.Form._get_translations>` Use
    :meth:`Meta.get_translations <wtforms.meta.DefaultMeta.get_translations>`
    instead.

* **Fields**

  * The ``TextField`` alias for 
    :class:`~wtforms.fields.StringField` is deprecated.

* **WTForms Extensions**
  All the extensions are being deprecated. We feel like the extensions we had
  would actually benefit from being pulled outside the WTForms package, 
  because it would allow them to have a separate release schedule that suits 
  their companion libraries.

  * :mod:`wtforms.ext.appengine` Is deprecated, see `WTForms-Appengine`_
  * :mod:`wtforms.ext.csrf` CSRF protection is now :doc:`built in <csrf>`
  * :mod:`wtforms.ext.dateutil` Is deprecated, but does not have a new home yet.
  * :mod:`wtforms.ext.django` Is deprecated, except for the templatetag which
    has moved. For fields and model_form, see `WTForms-Django`_
  * :mod:`wtforms.ext.i18n` i18n is now :doc:`built in <i18n>`
  * :mod:`wtforms.ext.sqlalchemy` Is deprecated, look at `WTForms-Alchemy`_ 
    (`docs <WTForms-Alchemy-docs>`_)

.. _WTForms-Alchemy: https://pypi.python.org/pypi/WTForms-Alchemy
.. _WTForms-Alchemy-docs: http://wtforms-alchemy.readthedocs.org/en/latest/
.. _WTForms-Appengine: https://github.com/wtforms/wtforms-appengine
.. _WTForms-Django: https://github.com/wtforms/wtforms-django