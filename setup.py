#!/usr/bin/env python
import wtforms  
import os
import ez_setup
from inspect import getdoc
ez_setup.use_setuptools()

from setuptools import setup, Feature

setup(
    name='WTForms',
    version='0.2dev',
    url='http://wtforms.simplecodes.com/',
    download_url='http://wtforms.simplecodes.com/',
    license='MIT',
    author='James Crasta, Thomas Johansson',
    author_email='jcrasta@gmail.com, prencher@gmail.com',
    description='HTTP/HTML forms handling for python',
    long_description=getdoc(wtforms),
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=['wtforms'],
    features={
        'ext': Feature('Extensions to WTForms providing extra functionality',
            standard=True,
            packages=['wtforms.ext']
        )
    },
    platforms=['any'],
    include_package_data=True,
)
