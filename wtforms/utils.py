"""
    wtforms.utils
    ~~~~~~~~~~~~~
    
    Various utility functions.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from cgi import escape

def html_params(**kwargs):
    """
    Generate HTML parameters for keywords
    """
    params = []
    keys = kwargs.keys()
    keys.sort()
    for k in keys:
        if k in ('class_', 'class__'):
            k = k[:-1]
        k = unicode(k)
        v = escape(unicode(kwargs[k]), quote=True)
        params.append(u'%s="%s"' % (k, v))
    return str.join(' ', params)

def partial(func, *args, **keywords):
    def newfunc(*fargs, **fkeywords):
        newkeywords = keywords.copy()
        newkeywords.update(fkeywords)
        return func(*(args + fargs), **newkeywords)
    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    return newfunc
