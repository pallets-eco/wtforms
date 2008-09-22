API
===

(TODO)

Basics
------

(TODO)

Forms
-----

Forms provide the highest level API in WTForms. They contain your field
definitions, delegate validation, take input, aggregate errors, and in
general function as the glue holding everything together.

Defining forms
~~~~~~~~~~~~~~

(TODO)

Using forms
~~~~~~~~~~~

(TODO)

Fields
------

Fields are responsible for rendering and data conversion. They delegate to
validators for data validation.

Field definitions
~~~~~~~~~~~~~~~~~

(TODO)

Built-in fields
~~~~~~~~~~~~~~~

(TODO)

Custom fields
~~~~~~~~~~~~~

(TODO)

Validators
----------

Validators simply takes an input, verifies it fulfills some criterion, such as
a maximum length for a string and returns. Or, if the validation fails, raises
a ValidationError. This system is very simple and flexible, and allows you to
chain any number of validators on fields.

Built-in validators
~~~~~~~~~~~~~~~~~~~

(TODO)

Custom validators
~~~~~~~~~~~~~~~~~

(TODO)
