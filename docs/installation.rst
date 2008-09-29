.. _installation:

Installation
============

To use WTForms, you will need **Python 2.4** or later. There are no external
dependencies for the core, but some :ref:`extensions <extensions>` may assume
certain libraries.


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


