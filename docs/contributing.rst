Contributing to WTForms
=======================

WTForms is an open-source library and changing and evolving over time.
To that end, we are supported by the contributions of many people in the
python community.


How to Contribute
-----------------

WTForms is now on `GitHub`_, so all contributions should be either associated
with a pull request or with a ticket & patch.

.. _GitHub: https://github.com/wtforms/wtforms


Contribution Guidelines
-----------------------

Code submitted should:

* Be formatted according to the `PEP8`_ style guideline **except** that it
  does not need to confirm to the 79-column limit requirement of the
  guideline.

* Have tests

  - Unless it's a bugfix, it should pass existing tests.
  - New classes or methods should mean new unit tests or extending existing
    tests.
  - Bugfixes can probably do with a regression test too (a test that would
    fail without this fix)

* Use naming schemes consistent with WTForms conventions

* Work on all versions of Python that WTForms currently supports.  Take
  advantage of `Github Actions`_ for running tests on all supported Python
  versions.

.. _Github Actions: https://github.com/wtforms/wtforms/actions
.. _PEP8: https://www.python.org/dev/peps/pep-0008/


Note on API compatibility
-------------------------

WTForms is a very small library, but yet it's possible to break API
compatibility pretty easily. We are okay with breaking API compatibility
for compelling features or major changes that we feel are worthwhile
inclusions to the WTForms core, but realize that any API compatibility
break will delay the inclusion of your ticket to the next major release.

Some examples of API compatibility breaks include:

* Adding new attributes or methods to the base Form class
* Modifying the number of required arguments of core methods like
  :meth:`~wtforms.fields.Field.process`
* Changing the default behavior of a field.

However, it is still possible to add new features to WTForms without breaking
API compatibility. For example, if one were looking to add Babel locale
support to DecimalField, it could be done so long as by default, DecimalField
behaved the same as it did before. This could look something like:

1. Add a keyword arg ``use_locale`` to the constructor
2. Make the keyword default to ``False`` so the behavior without this arg is
   identical to the previous behavior.
3. Add your functionality and make sure all existing DecimalField tests work
   unchanged (and of course add new tests for the new functionality).
