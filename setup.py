import sys

extra = {}

try:
    from setuptools import setup
    has_setuptools = True
    extra['test_suite'] = 'tests.runtests'
    extra['extras_require'] = {
        'Locale': ['Babel>=1.3'],
    }
except ImportError:
    from distutils.core import setup
    has_setuptools = False

if sys.version_info >= (3,) and not has_setuptools:
    raise Exception('Python 3 support requires setuptools.')

setup(
    name='WTForms',
    version='1.1dev',
    url='http://wtforms.simplecodes.com/',
    license='BSD',
    author='Thomas Johansson, James Crasta',
    author_email='wtforms@simplecodes.com',
    description='A flexible forms validation and rendering library for python web development.',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=[
        'wtforms',
        'wtforms.fields',
        'wtforms.widgets',
        'wtforms.ext',
        'wtforms.ext.appengine',
        'wtforms.ext.csrf',
        'wtforms.ext.dateutil',
        'wtforms.ext.django',
        'wtforms.ext.django.templatetags',
        'wtforms.ext.i18n',
        'wtforms.ext.sqlalchemy',
    ],
    package_data={
        'wtforms': ['locale/wtforms.pot', 'locale/*/*/*'],
    },
    **extra
)
