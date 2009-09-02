#!/usr/bin/env python
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

import ez_setup
from inspect import getdoc
ez_setup.use_setuptools()

from setuptools import setup, Feature

import wtforms

setup(
    name='WTForms',
    version='0.4',
    url='http://wtforms.simplecodes.com/',
    download_url='http://wtforms.simplecodes.com/',
    license='MIT',
    author='James Crasta, Thomas Johansson',
    author_email='jcrasta@gmail.com, prencher@gmail.com',
    description='HTTP/HTML forms handling for python',
    long_description=getdoc(wtforms),
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=[
        'wtforms',
        'wtforms.ext',
        'wtforms.ext.django',
        'wtforms.ext.django.templatetags',
        'wtforms.ext.sqlalchemy',
    ],
    platforms=['any'],
    include_package_data=True,
)
