"""
    wtforms.ext.django.fields
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Useful form fields for use with django ORM.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
from wtforms.fields import Field

class QuerySetSelectField(Field):
    """
    Given a QuerySet either at initialization or inside a view, will display a
    select drop-down field of choices. The `data` property actually will
    store/keep an ORM model instance, not the ID. Submitting a choice which is
    not in the queryset will result in a validation error. 

    Specifying `label_attr` in the constructor will use that property of the
    model instance for display in the list, else the model object's `__str__`
    or `__unicode__` will be used.

    If `allow_blank` is set to :const:`True`, then a blank choice will be added
    to the top of the list. Selecting this choice will result in the `data`
    property being :const:`None`.
    """
    def __init__(self, label=u'', validators=None, queryset=None, label_attr='', allow_blank=False, **kwargs):
        super(QuerySetSelectField, self).__init__(label, validators, **kwargs)
        self.label_attr = label_attr
        self.allow_blank = allow_blank
        self._set_data(None)
        if queryset is not None:
            self.queryset = queryset.all() # Make sure the queryset is fresh

    def _get_data(self):
        if self._formdata is not None:
            for obj in self.queryset:
                if obj.pk == self._formdata:
                    self._set_data(obj)
                    break
        return self._data

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def __call__(self, **kwargs):
        kwargs.setdefault('id', self.id)
        primary_key = self.queryset.model._meta.pk.name
        html = u'<select %s>' % html_params(name=self.name, **kwargs)
        if self.allow_blank:
            html += u'<option value="__None"></option>'
        for obj in queryset:
            pk = getattr(obj, primary_key)
            options = {'value': pk}
            if obj == self.data:
                options['selected'] = u'selected'
            label = self.label_attr and getattr(obj, self.label_attr) or obj
            html += u'<option %s>%s</option>' % (html_params(**options), escape(unicode(label)))
        html += u'</select>'
        return html

    def process_formdata(self, valuelist):
        if valuelist:
            if valuelist[0] == '__None':
                self.data = None
            else:
                self._formdata = int(valuelist[0])

    def pre_validate(self, form):
        if self.data is not None:
            for obj in self.queryset:
                if self.data == v:
                    break
            else:
                raise ValidationError('Not a valid choice')

class ModelSelectField(QuerySetSelectField):
    """
    Like a QuerySetSelectField, except takes a model class instead of a
    queryset and lists everything in it.
    """
    def __init__(self, label=u'', validators=None, model=None, **kwargs):
        super(ModelSelectField, self).__init__(label, validators, queryset=model._default_manager.all(), **kwargs)
