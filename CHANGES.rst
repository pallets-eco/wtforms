WTForms Changelog
=================

Version 1.1
-----------
Not yet released.

- Fix a bug in ORM modeling which would incorrectly raise a validation
  error for a valid, but boolean false input (for non-nullable columns).
- Move i18n into core. Deprecate `wtforms.ext.i18n`.
- Fix issue rendering SelectFields with value=True
- Make `DecimalField` able to use babel locale-based number formatting.
- Drop Python 3.2 support (Python3 support for 3.3+ only)

Version 1.0.5
-------------
Released September 10, 2013

- Fix a bug in validators which causes translations to happen once then
  clobber any future translations.
- ext.sqlalchemy / ext.appengine: minor cleanups / deprecation.
- Allow blank string and the string 'false' to be considered false values
  for BooleanField (configurable). This is technically a breaking change,
  but it is not likey to affect the majority of users adversely.
- ext.i18n form allows passing LANGUAGES to the constructor.

Version 1.0.4
-------------
Released April 28, 2013

- Add widgets and field implementations for HTML5 specialty input types.
- ext.appengine: Add NDB support.
- Add translations: Korean, Traditional Chinese

Version 1.0.3
-------------
Released January 24, 2013

- Tests complete in python 3.2/3.3.
- Localization for ru, fr.
- Minor fixes in documentation for clarity.
- FieldList now can take validators on the entire FieldList.
- ext.sqlalchemy model_form:

  * Fix issue with QuerySelectField
  * Fix issue in ColumnDefault conversion
  * Support Enum type

- Field class now allows traversal in Django 1.4 templates.

Version 1.0.2
-------------
Released August 24, 2012

- We now support Python 2.x and 3.x on the same codebase, thanks to a lot of
  hard work by Vinay Sajip.

- Add in ability to convert relationships to ext.sqlalchemy model_form

- Built-in localizations for more languages

- Validator cleanup:

  * Distinguish Required validator into InputRequired and DataRequired
  * Better IP address validation, including IPv6 support.
  * AnyOf / NoneOf now work properly formatting other datatypes than strings.
  * Optional validator can optionally pass through whitespace.


Version 1.0.1
-------------
Released February 29, 2012

- Fixed issues related to building for python 3 and python pre-releases.

- Add object_data to fields to get at the originally passed data.


Version 1.0
-----------
Released February 28, 2012

- Output HTML5 compact syntax by default.

- Substantial code reorg, cleanup, and test improvements

- Added ext.csrf for a way to implement CSRF protection

- ext.sqlalchemy:

  * Support PGInet, MACADDR, and UUID field conversion
  * Support callable defaults

- ext.appengine:

  * model_form now supports generating forms with the same ordering as model.
  * ReferencePropertyField now gets get_label like the other ORM fields

- Add localization support for WTForms built-in messages

- Python 3 support (via 2to3)

- Minor changes/fixes:

  * An empty label string can be specified on fields if desired
  * Option widget can now take kwargs customization
  * Field subclasses can provide default validators as a class property
  * DateTimeField can take time in microseconds
  * Numeric fields all set .data to None on coercion error for consistency.


Version 0.6.3
-------------
Released April 24, 2011

- Documentation: Substantial documentation improvements, including adding
  Crash Course as a sphinx document.

- ext.django: QuerySetSelectField (and ModelSelectField) now accept get_label
  similar to sqlalchemy equivalents.

- ext.appengine

  * model_form fixes: FloatField(#50), TimeField, DateTimeField(#55)
  * ReferencePropertyField: now properly stores model object, not key. (#48)


Version 0.6.2
-------------
Released January 22, 2011

- Bug Fixes:

  * ext.appengine: various field fixes (#34, #48), model_form changes (#41)
  * Fix issue in Optional with non-string input.
  * Make numeric fields more consistent.

- Tests: Improve test coverage substantially.

Version 0.6.1
-------------
Released September 17th, 2010

- Bug Fixes:

  * ext.appengine ReferencePropertyField (#36, #37)
  * dateutil fields: render issue (r419), and consistency issue (#35)
  * Optional validator failed when raw_data was absent (r418)

- Documentation: docs now mention HTML escaping functionality (#38)

- Add preliminary support for providing a translations object that can
  translate built-in validation and coercion errors (#32)


Version 0.6
-----------
Released April 25th, 2010.

- Widgets:

  * HTML is now marked as safe (using __html__) so that compatible templating
    engines will not auto-escape it.

- Fields:

  * Field._default is now Field.default.
  * All fields now have a `raw_data` property.
  * Fields which are select fields (including those in .ext) can be
    iterated to produce options, and have an option_widget kwarg.
  * Minor bugfixes and cleanup in FieldList, Select(Multiple)Field,
    QuerySelectField to address behavioral consistency.
  * Added FloatField, based on IntegerField.

- Extensions:

  * ext.appengine now supports FloatProperty and GeoPtProperty.
  * ext.sqlalchemy QueryMultipleSelectField changed to QuerySelectMultipleField.


Version 0.5
-----------
Released February 13th, 2010.

- Added a BaseForm class which provides the core processing and validation
  functionality of Form without requiring declarative subclassing.

- Fields:

  * Field labels now default to a humanized field name.
  * Fields now have a `short_name` property which is the un-prefixed name.
  * DecimalField now rounds values for display without float coercion.
    See docs for details on how to format decimals.

- Extensions:

  * ext.sqlalchemy.fields now has an additional QuerySelectMultipleField, and
    all fields can now support multiple-column primary keys.
  * ext.sqlalchemy.orm contains tools for making forms from ORM models.
  * Added ext.dateutil for flexible date-time parsing.
  * Added ext.appengine contributed by Rodrigo Moraes.

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

- `Form.auto_populate` and `Field.populate` were renamed to `populate_obj` to
  clarify that they populate another object, not the Form or Field. This is an
  API breaking change.

- Dropped support for Python 2.3.


Version 0.3.1
-------------
Released January 24th, 2009.

- Several fixes were made to the code and tests to make WTForms compatible
  with Python 2.3/2.4.

- Form's properties can now be accessed via dictionary-style access such as
  `form['author']`. This also has the intended effect of making variable
  lookups in Django templates more reliable.

- Form and Field construction changes: Form now uses a metaclass to handle
  creating its `_unbound_fields` property, and Field construction now gives an
  instance of the new `UnboundField` class instead of using a partial function
  application. These are both internal changes and do not change the API.


Version 0.3
-----------
Released January 18th, 2009.

- Validation overhaul: Fields are now responsible for their own validation,
  instead of mostly relying on Form. There are also new pre_validate and
  post_validate hooks on subfields, adding a great deal of flexibility when
  dealing with field-level validation. Note that this is an API breaking change
  if you have any subfields that override `Field.validate`. These will need to
  be updated to use the new hooks.

- Changes in how `process_data` and `process_formdata` are called:

    * `process_data` no longer accepts the `has_formdata` parameter.
    * At form instantiation time, `process_data` will be called only once for
      each field. If a model object is provided which contains the property,
      then this value is used. Otherwise, a keyword argument if specified is
      used. Failing that, the field's default value is used.
    * If any form data is sent, `process_formdata` will be called after
      `process_data` for each field. If no form data is available for the
      given field, it is called with an empty list.

- wtforms.ext.django has been overhauled, both to mirror features and changes
  of the Django 1.0 release, and to add some useful fields for working with
  django ORM data in forms.

- The `checker` keyword argument to SelectField, SelectMultipleField, and
  RadioField has been renamed to `coerce` to reflect the actual functionality
  of this callable.


Version 0.2
-----------
Released January 13th, 2009.

- We have documentation and unit tests!

- Fields now have a `flags` property which contain boolean flags that are set
  either by the field itself or validators being specified on a field. The
  flags can then be used in checks in template or python code.

- Changed the way fields take parameters, they are no longer quasi magic. This
  is a breaking change. Please see the documentation for the new syntax.

- Added optional description argument to Field, accessible on the field as
  `description`. This provides an easy way to define e.g. help text in the same
  place as the form.

- Added new semantics for validators which can stop the validation chain, with
  or without errors.

- Added a regexp validator, and removed the not_empty validator in favour of
  two validators, optional and required. The new validators allow control
  over the validation chain in addition to checking emptiness.

- Renamed wtforms.contrib to wtforms.ext and reorganised wtforms.ext.django.
  This is a breaking change if you were using the django extensions, but should
  only require changing your imports around a little.

- Better support for other frameworks such as Pylons.


Version 0.1
-----------
Released July 25th, 2008.

- Initial release.
