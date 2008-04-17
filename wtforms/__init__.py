"""
    wtforms
    ~~~~~~~
    
    What The Forms is a framework-agnostic way of generating HTML forms, handling
    form submissions, and validating it.

    Check out our trac wiki at http://dev.simplecodes.com/projects/wtforms
    
    :copyright: 2007-2008 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from wtforms.form import Form
from wtforms.fields import *
from wtforms.validators import ValidationError
from wtforms import validators

__version__ = "devel"
