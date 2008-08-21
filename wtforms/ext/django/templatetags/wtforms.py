"""
    wtforms.ext.django.templatetags.wtforms
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Template Tags for easy wtforms access in Django templates
    
    :copyright: 2007-2008 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from django import template
from django.template import resolve_variable
import re

class FormFieldNode(template.Node):
    def __init__(self, field_var, html_attrs):
        self.field_var = field_var
        self.html_attrs = html_attrs

    def render(self, context):
        base, field_name = self.field_var.rsplit('.', 1)
        field = getattr(resolve_variable(base, context), field_name)
        h_attrs = {}
        for k, v in self.html_attrs.iteritems():
            if v[0] in ('"', "'"):
                h_attrs[k] = v[1:-1]
            else:
                h_attrs[k] = resolve_variable(v, context)
        return field(**h_attrs)

def do_form_field(parser, token):
    """
    Render a WTForms form field allowing optional HTML attributes.
    Invocation looks like this:
      {% form_field form.username class="big_text" onclick=onclick_val %}
    where form.username is the path to the field value we want.  Any number 
    of key="value" arguments are supported. Unquoted values are resolved as
    template variables.
    """
    parts = token.contents.split(' ', 2)
    if len(parts) < 2:
        raise template.TemplateSyntaxError('%r tag must have the form field name as the first value, followed by optional key="value" attributes.' % parts[0])

    html_attrs = {}
    if len(parts) == 3:
        raw_args = list(args_split(parts[2]))
        if (len(raw_args) % 2) != 0:
            raise template.TemplateSyntaxError('%r tag received the incorrect number of key=value arguments.' % parts[0])
        for x in range(0, len(raw_args), 2):
            html_attrs[str(raw_args[x])] = raw_args[x+1]

    return FormFieldNode(parts[1], html_attrs)


register = template.Library()
register.tag('form_field', do_form_field)

# -- Utilities -------------------------------------------------------------

args_split_re = re.compile(ur'''("(?:[^"\\]*(?:\\.[^"\\]*)*)"|'(?:[^'\\]*(?:\\.[^'\\]*)*)'|[^\s=]+)''')
def args_split(text):
    """Split space-separated key=value arguments.  Keeps quoted strings intact.""" 
    for bit in args_split_re.finditer(text):
        bit = bit.group(0)
        if bit[0] == '"' and bit[-1] == '"':
            yield '"' + bit[1:-1].replace('\\"', '"').replace('\\\\', '\\') + '"'
        elif bit[0] == "'" and bit[-1] == "'":
            yield "'" + bit[1:-1].replace("\\'", "'").replace("\\\\", "\\") + "'"
        else:
            yield bit

