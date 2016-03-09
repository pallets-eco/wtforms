import sys
from setuptools import setup

extra = {}

if sys.version_info < (2, 7):
    extra['install_requires'] = ['ordereddict>=1.1']


setup(
    name='WTForms',
    version='3.0dev',
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
        'wtforms.csrf',
        'wtforms.fields',
        'wtforms.widgets',
    ],
    package_data={
        'wtforms': ['locale/wtforms.pot', 'locale/*/*/*'],
    },
    test_suite='tests.runtests',
    extras_require={
        'Locale': ['Babel>=1.3'],
        ':python_version=="2.6"': ['ordereddict'],
    },
    **extra
)
