What is WTForms?
================

[![Build Status](https://travis-ci.org/wtforms/wtforms.svg?branch=master)](https://travis-ci.org/wtforms/wtforms) [![Coverage Status](https://coveralls.io/repos/wtforms/wtforms/badge.svg?branch=master&service=github)](https://coveralls.io/github/wtforms/wtforms?branch=master) [![Documentation Status](https://readthedocs.org/projects/wtforms/badge/?version=latest)](http://wtforms.readthedocs.org/en/latest/?badge=latest)

WTForms is a flexible forms validation and rendering library for python web development.

To get started using WTForms, we recommend reading the [crash course][] on the docs site: http://wtforms.readthedocs.org/en/stable/

If you downloaded the package from PyPI, there will also be a prebuilt copy of the html documentation in the `docs/html/` directory.


Why use WTForms?
----------------

 * Security-first design; we take good validation seriously.
 * [Framework-agnostic][]; works with your web framework and template engine of choice.
 * Rich ecosystem of [library integrations](#library-integrations)

[crash course]: http://wtforms.readthedocs.org/en/stable/crash_course.html
[Framework-agnostic]: http://wtforms.readthedocs.org/en/stable/faq.html#does-wtforms-work-with-library-here


Installation
------------

The easiest way to install WTForms is using pip:

    pip install WTForms

If you downloaded a source tarball, or cloned the repository, you can install using setup.py:

    python setup.py install

You can also simply place the `wtforms` subdirectory somewhere on your python path. This can be useful if you deploy on Google App Engine for example.


Third-Party Library Integrations
--------------------------------

<a id="library-integrations" name="library-integrations"></a>
WTForms works with most web frameworks very well; but there are a number of tools available that make integration with database ORM's, environments, and frameworks even better - either reducing boilerplate or adding features like query fields, etc.

 * [Flask-WTF](https://flask-wtf.readthedocs.org/en/latest/) is an integration with the Flask framework providing a solid default CSRF configuration, file upload support, flask-i18n integration, and more.
 * [WTForms-Appengine](https://github.com/wtforms/wtforms-appengine) provides ORM-backed fields and form generation from Appengine db/ndb schema
 * [WTForms-SQLAlchemy](https://github.com/wtforms/wtforms-sqlalchemy) provides ORM-backed fields and generation of forms from models.
 * [WTForms-Alchemy](https://wtforms-alchemy.readthedocs.org/en/latest/) provides powerful model forms support 


