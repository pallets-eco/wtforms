"""
    wtforms.widgets
    ~~~~~~~~~~~~~~~
    
    The WTForms widget system.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from cgi import escape

__all__ = (
    'ListWidget', 'TextInput', 'PasswordInput', 'HiddenInput', 'CheckboxInput',
    'RadioInput', 'Textarea', 'Select'
)

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

class Widget(object):
    """
    Base class for all WTForms widgets.
    """
    def render(self, field, **kwargs):
        """
        Renders the widget. All widgets must implement this.
        
        `field`
            The field to render.
        `**kwargs`
            Any parameters used for rendering. Typically used to override or
            pass extra html attributes.
        """
        raise NotImplementedError()

class ListWidget(Widget):
    def __init__(self, parent_tag='ul', prefix_label=True):
        assert parent_tag in ('ol', 'ul')
        self.parent_tag = parent_tag
        self.prefix_label = prefix_label

    def render(self, field, **kwargs):
        html = [u'<%s %s>' % (self.parent_tag, html_params(**kwargs))]
        for subfield in field:
            if self.prefix_label:
                html.append(u'<li>%s: %s</li>' % (subfield.label, subfield()))
            else:
                out.append(u'<li>%s%s</li>' % (subfield(), subfield.label))
        html.append(u'</%s>' % self.parent_tag)
        return ''.join(html)

class Input(Widget):
    pass

class TextInput(Input):
    pass
    
class PasswordInput(Input):
    pass

class HiddenInput(Input):
    pass

class CheckboxInput(Input):
    pass

class RadioInput(Input):
    pass

class Textarea(Widget):
    pass

class Select(Widget):
    pass
