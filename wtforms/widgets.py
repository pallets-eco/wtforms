"""
    wtforms.widgets
    ~~~~~~~~~~~~~~~
    
    The WTForms widget system.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from cgi import escape

__all__ = (
    'CheckboxInput', 'FileInput', 'HiddenInput', 'ListWidget', 'PasswordInput',
    'RadioInput', 'Select', 'SubmitInput', 'TextArea', 'TextInput',
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
    def __init__(self, html_tag='ul', prefix_label=True):
        assert html_tag in ('ol', 'ul')
        self.html_tag = html_tag
        self.prefix_label = prefix_label

    def render(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = [u'<%s %s>' % (self.html_tag, html_params(**kwargs))]
        for subfield in field:
            if self.prefix_label:
                html.append(u'<li>%s: %s</li>' % (subfield.label, subfield()))
            else:
                html.append(u'<li>%s %s</li>' % (subfield(), subfield.label))
        html.append(u'</%s>' % self.html_tag)
        return ''.join(html)

class Input(Widget):
    def __init__(self, input_type=None):
        if input_type is not None:
            self.input_type = input_type

    def render(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        return u'<input %s />' % html_params(name=field.name, **kwargs)

class TextInput(Input):
    input_type = 'text'
    
class PasswordInput(Input):
    input_type = 'password'

    def __init__(self, hide_value=True):
        self.hide_value = hide_value

    def render(self, field, **kwargs): 
        if self.hide_value:
            kwargs['value'] = ''
        return super(PasswordInput, self).render(field, **kwargs)

class HiddenInput(Input):
    input_type = 'hidden'

class CheckboxInput(Input):
    input_type = 'checkbox'

    def render(self, field, **kwargs): 
        kwargs.setdefault('value', u'y')
        if field.data:
            kwargs['checked'] = u'checked'
        return super(CheckboxInput, self).render(field, **kwargs)

class RadioInput(Input):
    input_type = 'radio'

    def render(self, field, **kwargs):
        if field.checked:
            kwargs['checked'] = u'checked'
        return super(RadioInput, self).render(field, value=field.data, **kwargs)
        
class FileInput(Input):
    input_type = 'file'

class SubmitInput(Input):
    input_type = 'submit'

    def render(self, field, **kwargs): 
        kwargs.setdefault('value', field.label.text)
        return super(SubmitInput, self).render(field, **kwargs)

class TextArea(Widget):
    def render(self, field, **kwargs): 
        kwargs.setdefault('id', field.id)
        return u'<textarea %s>%s</textarea>' % (html_params(name=field.name, **kwargs), escape(unicode(field._value())))

class Select(Widget):
    def __init__(self, multiple=False):
        self.multiple = multiple
        
    def render(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = 'multiple'
        html = u'<select %s>' % html_params(name=field.name, **kwargs)
        for val,title in field.choices:
            options = {'value': val}
            if field._selected(val):
                options['selected'] = u'selected'
            html += u'<option %s>%s</option>' % (html_params(**options), escape(unicode(title)))
        html += u'</select>'
        return html
