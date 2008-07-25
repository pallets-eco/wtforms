"""
    wtforms
    ~~~~~~~
    
    WTForms is a HTTP/HTML forms handling library, written in Python.
    
    It handles definition, validation and rendering in a flexible and i18n
    friendly way. It heavily reduces boilerplate and is completely unicode
    aware.

    Check out the hg repository at http://www.bitbucket.org/prencher/wtforms/.
    
    :copyright: 2007-2008 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from wtforms.form import Form
from wtforms.fields import *
from wtforms.validators import ValidationError
from wtforms import validators

__version__ = "0.2dev"
