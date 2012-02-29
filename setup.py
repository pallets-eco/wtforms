import os, sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

extra = {}

try:
    from setuptools import setup
    has_setuptools = True
    extra['test_suite'] = 'tests.runtests'
except ImportError:
    from distutils.core import setup
    has_setuptools = False

if sys.version_info >= (3, ):
    if not has_setuptools:
        raise Exception('Python3 support in WTForms requires distribute.')
    extra['use_2to3'] = True
    extra['use_2to3_exclude_fixers'] = ['lib2to3.fixes.fix_filter', 'lib2to3.fixes.filter']

setup(
    name='WTForms',
    version='1.0.2',
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
        'wtforms.ext.i18n': ['messages/wtforms.pot', 'messages/*/*/*'],
    },
    **extra
)
