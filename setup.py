# -*- coding: utf-8 -*-
import wtforms  
import os
import ez_setup
from inspect import getdoc
ez_setup.use_setuptools()

from setuptools import setup, Feature

setup(
    name='WTForms',
    version='0.1',
    url='http://dev.simplecodes.com/projects/wtforms',
    download_url='http://dev.simplecodes.com/hg/wtforms', #FIXME
    license='MIT',
    author='James Crasta, Thomas Johansson',
    author_email='jcrasta@simplecodes.com, thomas@simplecodes.com',
    description='Forms framework designed to work with multiple web',
    long_description=getdoc(wtforms),
    zip_safe=False,
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
    platforms=['any'],
    include_package_data=True,
)
