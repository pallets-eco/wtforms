import os, sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from distutils.core import setup
import wtforms

setup(
    name='WTForms',
    version=wtforms.__version__,
    url='http://wtforms.simplecodes.com/',
    license='BSD',
    author='Thomas Johansson',
    author_email='prencher@gmail.com',
    description='A flexible forms validation and rendering library for python web development',
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
        'wtforms.ext',
        'wtforms.ext.django',
        'wtforms.ext.django.templatetags',
        'wtforms.ext.sqlalchemy',
    ]
)
