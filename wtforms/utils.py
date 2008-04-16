"""
    wtforms.utils
    ~~~~~~~~~~~~~
    
    TODO
    
    :copyright: 2007-2008 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""

def partial(func, *args, **keywords):
    def newfunc(*fargs, **fkeywords):
        newkeywords = keywords.copy()
        newkeywords.update(fkeywords)
        return func(*(args + fargs), **newkeywords)
    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    return newfunc
