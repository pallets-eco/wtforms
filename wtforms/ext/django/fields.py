"""
    wtforms.ext.django.fields
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Useful form fields for use with django ORM.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from wtforms.fields import Field

class QSChoices(object):
    """
    Iterable which yields a set of (id, object) pairs given a queryset.

    if `label_attr` is specified, instead yield (id, getattr(object, label_attr)). 
    """
    def __init__(self, queryset, label_attr=None):
        self.queryset = queryset
        self.pk_attr = queryset.model._meta.pk.name
        self.label_attr = label_attr
        
    def __iter__(self):
        if self._label_attr:
            for entry in self.queryset:
                yield (getattr(entry, self.pk_attr), getattr(entry, self.label_attr))
        else:
            for entry in self.queryset:
                yield (getattr(entry, self.pk_attr), entry)

    def __contains__(self, key):
        for entry in self._queryset:
            if getattr(entry, self.pk_attr) == key:
                return True
        return False
            
class QuerySetSelectField(Field):
    def __init__(self, label=u'', validators=None, queryset=None, **kwargs):
        super(ORMSelectField, self).__init__(label, validators, **kwargs)
        self._formdata = None
        self._data = None
        if queryset is not None:
            self.queryset = queryset.all() # Make sure the queryset is fresh

    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        primary_key = self.queryset.model._meta.pk.name
        html = u'<select %s>' % html_params(name=self.name, **kwargs)
        for obj in queryset:
            pk = getattr(obj, primary_key)
            options = {'value': pk}
            if obj == self.data:
                options['selected'] = u'selected'
            html += u'<option %s>%s</option>' % (html_params(**options), escape(unicode(title)))
        html += u'</select>'
        return html

    def process_formdata(self, valuelist):
        if valuelist:
            self._formdata = int(valuelist[0])

    def validate(self, *args):
        for obj in self.queryset:
            if self.data == v:
                break
        else:
            raise ValidationError('Not a valid choice')

    def _get_data(self):
        if self._formdata is not None:
            primary_key = self.queryset.model._meta.pk.name
            for obj in self.queryset:
                if getattr(obj, primary_key) == self._formdata:
                    self._set_data(obj)
                    break
        return self._data

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

class ModelSelectField(QuerySetSelectField):
    def __init__(self, label=u'', validators=None, model=None, **kwargs):
        super(ModelSelectField, self).__init__(label, validators, queryset=model.objects.all())
