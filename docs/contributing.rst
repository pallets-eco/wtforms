Contributing to WTForms
=======================

WTForms is an open-source library and changing and evolving over time.
To that end, we are supported by the contributions of many people in the
python community.


How to Contribute
-----------------

WTForms is now on GitHub, so all contributions should be either associated
with a pull request or with a ticket & patch.


Contribution Guidelines
-----------------------

Code submitted should:

* Be formatted according to the `PEP8`_ style guideline **except** that it 
  does not need to confirm to the 79-column limit requirement of the 
  guideline.

* Have unit tests

  - Unless it's a bugfix, it should pass existing unit tests.
  - New classes or methods should mean new unit tests or extending existing
    tests.
  - Bugfixes can probably do with a regression test too (a test that would 
    fail without this fix)

* Use naming schemes consistent with WTForms conventions

* Work on all versions of Python that WTForms currently supports (and 
  python3 without needing 2to3).  Take advantage of `Travis-CI`_ for running
  tests on all supported Python versions.

.. _Travis-CI: http://travis-ci.org
.. _PEP8: http://www.python.org/dev/peps/pep-0008/