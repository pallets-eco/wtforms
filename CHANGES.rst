.. currentmodule:: wtforms

WTForms Changelog
=================


Version 3.0
-----------

Unreleased

-   HTML is escaped using MarkupSafe instead of the previous internal
    implementation. :func:`~widgets.core.escape_html` is removed,
    replaced by :func:`markupsafe.escape`.
    :class:`~widgets.core.HTMLString` is removed, replaced by
    :class:`markupsafe.Markup`. (`#400`_)
-   ``aria_`` args are rendered the same way as ``data_`` args, by
    converting underscores to hyphens. ``aria_describedby="name-help"``
    becomes ``aria-describedby="name-help"``. (`#239`_, `#389`_)
-   HTML5 :class:`~fields.html5.IntegerField` and
    :class:`~fields.html5.RangeInput` don't render the ``step="1"``
    attribute by default. (`#343`_)
-   The :class:`~widgets.TextArea` widget prepends a ``\r\n`` newline
    when rendering to account for browsers stripping an initial line for
    display. This does not affect the value. (`#238`_, `#395`_)
-   :class:`~fields.core.Label` text is escaped before rendering.
    (`#315`_, `#375`_)
-   :class:`~fields.StringField` sets ``data`` to ``None`` when form
    data is empty and an initial value was not provided. Although it
    previously set an empty string, ``None`` is consistent with the
    behavior of other fields. (`#355`_)
-   :class:`~fields.SelectField` no longer coerces ``None`` to ``"None"``
    allowing use of ``"None"`` as an option (`#288`_, `#289`_)
-   :class:`~validators.Length` gives a more helpful error message when
    ``min`` and ``max`` are the same value (`#266`_)
-   Added more documentation on HTML5 fields and corrected related tests
    (`#326`_, `#409`_)
-   Added a ``check_validators`` method to :class:`~fields.Field` which checks
    if the given validators are both callable, and not classes (`#298`_, `#410`_)
-   Fixed broken IPv6 validator, validation now uses the ``ipaddress`` package
    (`#385`_, `#403`_)
-   ``FieldList`` error list is keeps entries in orders for easier identifcation
    of erroring fields (`#257`_, `#407`_)
-   Converted certain tests to use PyTest style (`#413`_, `#422`_)
-   Black is now used for code formatting (`#399`_, `#415`_)
-   Fixed :class:`~validators.IPAddress` docstring typo and conformed line lengths to PEP8 (`#418`_)
-   Fixed some small formatting issues in tests (`#420`_)
-   Enabled Flake8 (`#416`_, `#423`_)
-   Moved WTForms to the ``src`` directory (`#397`_, `#424`_)
-   Specified version of Babel required for setup to avoid errors (`#430`_)
-   Updated Ukrainian translation (`#433`_)
-   Email validation is now handled by an optional library, ``email_validator`` (`#429`_)
-   Fixed broken format string in Arabic translation (`#471`_)
-   Replaced usage of ``getattr``/``setattr`` with constant attributes with
    regular variable accesses (`#482`_, `#484`_)
-   Updated ``false_values`` param in ``BooleanField`` docs (`#483`_, `#485`_)

.. _#238: https://github.com/wtforms/wtforms/issues/238
.. _#239: https://github.com/wtforms/wtforms/issues/239
.. _#257: https://github.com/wtforms/wtforms/issues/257
.. _#266: https://github.com/wtforms/wtforms/pull/266
.. _#288: https://github.com/wtforms/wtforms/pull/288
.. _#289: https://github.com/wtforms/wtforms/issues/289
.. _#298: https://github.com/wtforms/wtforms/pull/298
.. _#315: https://github.com/wtforms/wtforms/pull/315
.. _#326: https://github.com/wtforms/wtforms/pull/326
.. _#343: https://github.com/wtforms/wtforms/pull/343
.. _#355: https://github.com/wtforms/wtforms/pull/355
.. _#375: https://github.com/wtforms/wtforms/pull/375
.. _#385: https://github.com/wtforms/wtforms/issues/385
.. _#389: https://github.com/wtforms/wtforms/pull/389
.. _#395: https://github.com/wtforms/wtforms/pull/395
.. _#397: https://github.com/wtforms/wtforms/issues/397
.. _#399: https://github.com/wtforms/wtforms/issues/399
.. _#400: https://github.com/wtforms/wtforms/pull/400
.. _#403: https://github.com/wtforms/wtforms/pull/403
.. _#407: https://github.com/wtforms/wtforms/pull/407
.. _#409: https://github.com/wtforms/wtforms/pull/409
.. _#410: https://github.com/wtforms/wtforms/pull/410
.. _#413: https://github.com/wtforms/wtforms/pull/413
.. _#415: https://github.com/wtforms/wtforms/pull/415
.. _#416: https://github.com/wtforms/wtforms/issues/416
.. _#418: https://github.com/wtforms/wtforms/pull/418
.. _#420: https://github.com/wtforms/wtforms/pull/420
.. _#422: https://github.com/wtforms/wtforms/pull/422
.. _#423: https://github.com/wtforms/wtforms/pull/423
.. _#424: https://github.com/wtforms/wtforms/pull/424
.. _#429: https://github.com/wtforms/wtforms/pull/429
.. _#430: https://github.com/wtforms/wtforms/pull/430
.. _#433: https://github.com/wtforms/wtforms/pull/433
.. _#471: https://github.com/wtforms/wtforms/pull/471
.. _#482: https://github.com/wtforms/wtforms/issues/482
.. _#483: https://github.com/wtforms/wtforms/issues/483
.. _#484: https://github.com/wtforms/wtforms/pull/484
.. _#485: https://github.com/wtforms/wtforms/pull/485



Version 2.2.1
-------------

Released on June 7th, 2018

-   :class:`~fields.StringField` only sets ``data = ''`` when form data
    is empty and an initial value was not provided. This fixes an issue
    where the default value wasn't rendered with the initial form.
    (`#291`_, `#401`_)

.. _#291: https://github.com/wtforms/wtforms/issues/291
.. _#401: https://github.com/wtforms/wtforms/issues/401


Version 2.2
-----------

Released on June 2nd, 2018

-   Merged new and updated translations from the community.
-   Passing ``data_`` args to render a field converts all the
    underscores to hyphens when rendering the HTML attribute, not just
    the first one. ``data_foo_bar`` becomes ``data-foo-bar``. (`#248`_)
-   The :class:`~validators.UUID` validator uses the :class:`uuid.UUID`
    class instead of a regex. (`#251`_)
-   :class:`~fields.SelectField` copies the list of ``choices`` passed
    to it so modifying an instance's choices will not modify the global
    form definition. (`#286`_)
-   Fields call :meth:`~fields.Field.process_formdata` even if the raw
    data is empty. (`#280`_)
-   Added a :class:`~fields.MultipleFileField` to handle a multi-file
    input. :class:`~fields.FileField` continues to handle only one
    value. The underlying :class:`~widgets.FileInput` widget gained a
    ``multiple`` argument. (`#281`_)
-   :class:`~fields.SelectField` choices can contain HTML (MarkupSafe
    ``Markup`` object or equivalent API) and will be rendered properly.
    (`#302`_)
-   :class:`~fields.TimeField` and
    :class:`html5.TimeField <fields.html5.TimeField>` were added.
    (`#254`_)
-   Improved :class:`~validators.Email`. Note that it is still
    unreasonable to validate all emails with a regex and you should
    prefer validating by actually sending an email. (`#294`_)
-   Widgets render the ``required`` attribute when using a validator
    that provides the ``'required'`` flag, such as
    :class:`~validators.DataRequired`. (`#361`_)
-   Fix a compatibility issue with SQLAlchemy 2.1 that caused
    :class:`~ext.sqlalchemy.fields.QuerySelectField` to fail with
    ``ValueError: too many values to unpack``. (`#391`_)

.. _#248: https://github.com/wtforms/wtforms/pull/248
.. _#251: https://github.com/wtforms/wtforms/pull/251
.. _#254: https://github.com/wtforms/wtforms/pull/254
.. _#280: https://github.com/wtforms/wtforms/pull/280
.. _#281: https://github.com/wtforms/wtforms/pull/281
.. _#286: https://github.com/wtforms/wtforms/pull/286
.. _#294: https://github.com/wtforms/wtforms/pull/294
.. _#302: https://github.com/wtforms/wtforms/pull/302
.. _#361: https://github.com/wtforms/wtforms/pull/361
.. _#391: https://github.com/wtforms/wtforms/pull/391


Version 2.1
-----------

Released December 15, 2015

- Added ``render_kw`` to allow default rendering time options.
- Updated / added a number of localizations
- Updated docs
- Allow widgets to set flags


Version 2.0.2
-------------

Released January 18, 2015

- Added more localizations and updated some.
- Validators for email and URL can validate IDNA-encoded domain names and new TLDs
- Better ``DeprecationWarnings``
- Support localization files in ``/usr/share/locale`` (for distro packaging)


Version 2.0.1
-------------

Released July 1, 2014

- Update wheel install to conditionally install ordereddict for python 2.6.
- Doc improvements


Version 2.0
-----------

Released May 20, 2014

- Add new ``class Meta`` paradigm for much more powerful customization
  of WTForms.
- Move i18n into core. Deprecate ``wtforms.ext.i18n``.
- Move CSRF into core. Deprecate ``wtforms.ext.csrf``.
- Fix issue rendering SelectFields with ``value=True``
- Make ``DecimalField`` able to use babel locale-based number formatting.
- Drop Python 3.2 support (Python3 support for 3.3+ only)
- passing ``attr=False`` to WTForms widgets causes the value to be ignored.
- ``Unique`` validator in ``wtforms.ext.sqlalchemy`` has been removed.


Version 1.0.5
-------------

Released September 10, 2013

- Fix a bug in validators which causes translations to happen once then
  clobber any future translations.
- ``ext.sqlalchemy`` / ``ext.appengine``: minor cleanups / deprecation.
- Allow blank string and the string ``false`` to be considered false values
  for ``BooleanField`` (configurable). This is technically a breaking change,
  but it is not likey to affect the majority of users adversely.
- ``ext.i18n`` form allows passing ``LANGUAGES`` to the constructor.


Version 1.0.4
-------------

Released April 28, 2013

- Add widgets and field implementations for HTML5 specialty input types.
- ``ext.appengine``: Add NDB support.
- Add translations: Korean, Traditional Chinese


Version 1.0.3
-------------

Released January 24, 2013

- Tests complete in python 3.2/3.3.
- Localization for ru, fr.
- Minor fixes in documentation for clarity.
- ``FieldList`` now can take validators on the entire ``FieldList``.
- ``ext.sqlalchemy`` model_form:

  * Fix issue with ``QuerySelectField``
  * Fix issue in ``ColumnDefault`` conversion
  * Support ``Enum`` type

- Field class now allows traversal in Django 1.4 templates.


Version 1.0.2
-------------

Released August 24, 2012

- We now support Python 2.x and 3.x on the same codebase, thanks to a lot of
  hard work by Vinay Sajip.

- Add in ability to convert relationships to ``ext.sqlalchemy`` ``model_form``

- Built-in localizations for more languages

- Validator cleanup:

  * Distinguish ``Required`` validator into ``InputRequired`` and ``DataRequired``
  * Better IP address validation, including IPv6 support.
  * ``AnyOf`` / ``NoneOf`` now work properly formatting other datatypes than strings.
  * ``Optional`` validator can optionally pass through whitespace.


Version 1.0.1
-------------

Released February 29, 2012

- Fixed issues related to building for python 3 and python pre-releases.

- Add ``object_data`` to fields to get at the originally passed data.


Version 1.0
-----------

Released February 28, 2012

- Output HTML5 compact syntax by default.

- Substantial code reorg, cleanup, and test improvements

- Added ``ext.csrf`` for a way to implement CSRF protection

- ``ext.sqlalchemy``:

  * Support ``PGInet``, ``MACADDR``, and ``UUID`` field conversion
  * Support callable defaults

- ``ext.appengine``:

  * model_form now supports generating forms with the same ordering as model.
  * ReferencePropertyField now gets get_label like the other ORM fields

- Add localization support for WTForms built-in messages

- Python 3 support (via 2to3)

- Minor changes/fixes:

  * An empty label string can be specified on fields if desired
  * ``Option`` widget can now take kwargs customization
  * Field subclasses can provide default validators as a class property
  * ``DateTimeField`` can take time in microseconds
  * Numeric fields all set ``.data`` to ``None`` on coercion error for consistency.


Version 0.6.3
-------------
Released April 24, 2011

- Documentation: Substantial documentation improvements, including adding
  Crash Course as a sphinx document.

- ``ext.django``: ``QuerySetSelectField`` (and ``ModelSelectField``) now accept ``get_label``
  similar to sqlalchemy equivalents.

- ``ext.appengine``

  * model_form fixes: ``FloatField`` (#50), ``TimeField``, ``DateTimeField`` (#55)
  * ``ReferencePropertyField``: now properly stores model object, not key. (#48)


Version 0.6.2
-------------

Released January 22, 2011

- Bug Fixes:

  * ``ext.appengine``: various field fixes (#34, #48), ``model_form`` changes (#41)
  * Fix issue in ``Optional`` with non-string input.
  * Make numeric fields more consistent.

- Tests: Improve test coverage substantially.


Version 0.6.1
-------------

Released September 17th, 2010

- Bug Fixes:

  * ``ext.appengine ReferencePropertyField`` (#36, #37)
  * dateutil fields: render issue (r419), and consistency issue (#35)
  * Optional validator failed when raw_data was absent (r418)

- Documentation: docs now mention HTML escaping functionality (#38)

- Add preliminary support for providing a translations object that can
  translate built-in validation and coercion errors (#32)


Version 0.6
-----------

Released April 25th, 2010.

- Widgets:

  * HTML is now marked as safe (using ``__html__``) so that compatible templating
    engines will not auto-escape it.

- Fields:

  * ``Field._default`` is now ``Field.default``.
  * All fields now have a ``raw_data`` property.
  * Fields which are select fields (including those in ``.ext``) can be
    iterated to produce options, and have an ``option_widget`` kwarg.
  * Minor bugfixes and cleanup in ``FieldList``, ``Select(Multiple)Field``,
    ``QuerySelectField`` to address behavioral consistency.
  * Added ``FloatField``, based on ``IntegerField``.

- Extensions:

  * ext.appengine now supports FloatProperty and GeoPtProperty.
  * ext.sqlalchemy QueryMultipleSelectField changed to QuerySelectMultipleField.


Version 0.5
-----------

Released February 13th, 2010.

- Added a ``BaseForm`` class which provides the core processing and validation
  functionality of ``Form`` without requiring declarative subclassing.

- Fields:

  * Field labels now default to a humanized field name.
  * Fields now have a ``short_name`` property which is the un-prefixed name.
  * ``DecimalField`` now rounds values for display without float coercion.
    See docs for details on how to format decimals.

- Extensions:

  * ``ext.sqlalchemy.fields`` now has an additional ``QuerySelectMultipleField``, and
    all fields can now support multiple-column primary keys.
  * ``ext.sqlalchemy.orm`` contains tools for making forms from ORM models.
  * Added ``ext.dateutil`` for flexible date-time parsing.
  * Added ``ext.appengine`` contributed by Rodrigo Moraes.

- Added AnyOf and NoneOf validators.


Version 0.4
-----------

Released October 10th, 2009.

- Fields have much greater control over input processing. Filters have been
  added to implement a simple way to transform input data.

- Added fields that encapsulate advanced data structures such as dynamic lists
  or child forms for more powerful field composing.

- Fields now use widgets for rendering.

- All built-in validators have been converted to classes to clean up the code.

- ``Form.auto_populate`` and ``Field.populate`` were renamed to ``populate_obj`` to
  clarify that they populate another object, not the Form or Field. This is an
  API breaking change.

- Dropped support for Python 2.3.


Version 0.3.1
-------------

Released January 24th, 2009.

- Several fixes were made to the code and tests to make WTForms compatible
  with Python 2.3/2.4.

- Form's properties can now be accessed via dictionary-style access such as
  ``form['author']``. This also has the intended effect of making variable
  lookups in Django templates more reliable.

- Form and Field construction changes: Form now uses a metaclass to handle
  creating its ``_unbound_fields`` property, and Field construction now gives an
  instance of the new ``UnboundField`` class instead of using a partial function
  application. These are both internal changes and do not change the API.


Version 0.3
-----------

Released January 18th, 2009.

- Validation overhaul: Fields are now responsible for their own validation,
  instead of mostly relying on ``Form``. There are also new ``pre_validate`` and
  ``post_validate`` hooks on subfields, adding a great deal of flexibility when
  dealing with field-level validation. Note that this is an API breaking change
  if you have any subfields that override ``Field.validate``. These will need to
  be updated to use the new hooks.

- Changes in how ``process_data`` and ``process_formdata`` are called:

    * ``process_data`` no longer accepts the ``has_formdata`` parameter.
    * At form instantiation time, ``process_data`` will be called only once for
      each field. If a model object is provided which contains the property,
      then this value is used. Otherwise, a keyword argument if specified is
      used. Failing that, the field's default value is used.
    * If any form data is sent, ``process_formdata`` will be called after
      ``process_data`` for each field. If no form data is available for the
      given field, it is called with an empty list.

- ``wtforms.ext.django`` has been overhauled, both to mirror features and changes
  of the Django 1.0 release, and to add some useful fields for working with
  django ORM data in forms.

- The ``checker`` keyword argument to ``SelectField``, ``SelectMultipleField``, and
  ``RadioField`` has been renamed to ``coerce`` to reflect the actual functionality
  of this callable.


Version 0.2
-----------

Released January 13th, 2009.

- We have documentation and unit tests!

- Fields now have a ``flags`` property which contain boolean flags that are set
  either by the field itself or validators being specified on a field. The
  flags can then be used in checks in template or python code.

- Changed the way fields take parameters, they are no longer quasi magic. This
  is a breaking change. Please see the documentation for the new syntax.

- Added optional description argument to Field, accessible on the field as
  ``description``. This provides an easy way to define e.g. help text in the same
  place as the form.

- Added new semantics for validators which can stop the validation chain, with
  or without errors.

- Added a regexp validator, and removed the not_empty validator in favour of
  two validators, optional and required. The new validators allow control
  over the validation chain in addition to checking emptiness.

- Renamed ``wtforms.contrib`` to ``wtforms.ext`` and reorganised ``wtforms.ext.django``.
  This is a breaking change if you were using the django extensions, but should
  only require changing your imports around a little.

- Better support for other frameworks such as Pylons.


Version 0.1
-----------

Released July 25th, 2008.

- Initial release.
