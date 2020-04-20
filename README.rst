WTForms
=======

.. image:: https://travis-ci.org/wtforms/wtforms.svg?branch=master
    :target: https://travis-ci.org/wtforms/wtforms
    :alt: Continuous Integration status
.. image:: https://coveralls.io/repos/github/wtforms/wtforms/badge.svg?branch=master
    :target: https://coveralls.io/github/wtforms/wtforms?branch=master
    :alt: Coverage status
.. image:: https://readthedocs.org/projects/wtforms/badge/?version=stable
    :target: https://wtforms.readthedocs.io/en/stable/?badge=stable
    :alt: Documentation status
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

WTForms is a flexible forms validation and rendering library for Python
web development. It is `framework agnostic`_ and can work with whatever
web framework and template engine you choose. There are various
community libraries that provide closer integration with popular
frameworks.

To get started using WTForms, we recommend reading the `crash course`_
in the docs.

.. _crash course: https://wtforms.readthedocs.io/en/stable/crash_course.html
.. _framework agnostic: https://wtforms.readthedocs.io/en/stable/faq.html#does-wtforms-work-with-library-here


Installation
------------

Install and update using pip::

    pip install -U WTForms


Third-Party Library Integrations
--------------------------------

WTForms is designed to work with any web framework and template engine.
There are a number of community-provided libraries that make integrating
with frameworks even better.

-   `Flask-WTF`_ integrates with the Flask framework. It can
    automatically load data from the request, uses Flask-Babel to
    translate based on user-selected locale, provides full-application
    CSRF, and more.
-   `WTForms-Alchemy`_ provides rich support for generating forms from
    SQLAlchemy models, including an expanded set of fields and
    validators.
-   `WTForms-SQLAlchemy`_ provides ORM-backed fields and form generation
    from SQLAlchemy models.
-   `WTForms-AppEngine`_ provides ORM-backed fields and form generation
    from AppEnding db/ndb schema
-   `WTForms-Django`_ provides ORM-backed fields and form generation
    from Django models, as well as integration with Django's I18N
    support.

.. _Flask-WTF: https://flask-wtf.readthedocs.io/
.. _WTForms-Alchemy: https://wtforms-alchemy.readthedocs.io/
.. _WTForms-SQLAlchemy: https://github.com/wtforms/wtforms-sqlalchemy
.. _WTForms-AppEngine: https://github.com/wtforms/wtforms-appengine
.. _WTForms-Django: https://github.com/wtforms/wtforms-django


Links
-----

-   Documentation: https://wtforms.readthedocs.io/
-   License: `BSD <https://github.com/wtforms/wtforms/blob/master/LICENSE>`_
-   Releases: https://pypi.org/project/WTForms/
-   Code: https://github.com/wtforms/wtforms
-   Issue tracker: https://github.com/wtforms/wtforms/issues
-   Test status:

    -   Linux: https://travis-ci.org/wtforms/wtforms

-   Test coverage: https://coveralls.io/github/wtforms/wtforms
