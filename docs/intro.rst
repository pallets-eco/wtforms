.. _intro:

Introduction
============

So you've cracked your knuckles and started working on that awesome python
webapp you want to write.  Probably it's a blog. Everyone writes a blog as their
first webapp. At some point in time though, your blog goes beyond basic input
and you start thinking about form handling. Enter WTForms.

But why do I need *another* stinking framework? Well, some webapp frameworks
take the approach of associating database models with form handling. While this
can be handy for very basic create/update views, chances are you'll need more
functionality than that. Or maybe you have a generic form handling framework but
you want to customize the HTML generation of those form fields, and define your
own validation. 

With WTForms, your form field HTML can be generated for you, but we let you
customize it in your templates.  This allows you to maintain separation of code
and presentation, and keep those messy parameters out of your python code.
Because we strive for loose coupling, you should be able to do that in any
templating engine you like, as well.  To see examples of how it works, check out
our :ref:`crashcourse`.

Prerequisites
-------------

To use WTForms, you will need **Python 2.4** or later. There are no external
dependencies for the core, but some :ref:`extensions <extensions>` may assume
certain libraries.

.. _installation:

Installation
------------

The most recent release is always available in the `cheeseshop`_ and can be
installed using `easy_install`_::

    easy_install WTForms

Alternately, you can also install the development version:

1. Install `Mercurial`_
2. ``hg clone http://dev.simplecodes.com/hg/wtforms``
3. ``cd wtforms``
4. ``python setup.py develop``

Step 4 will install wtforms as a development package via setuptools. This
will make it available in your python path. Alternately you can copy or symlink
the wtforms subdirectory into your site-packages directory.

.. _cheeseshop: http://pypi.python.org/pypi/WTForms/
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _Mercurial: http://www.selenic.com/mercurial/

