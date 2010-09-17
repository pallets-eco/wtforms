"""
Useful form fields for use with the Django ORM.
"""
from wtforms import widgets
from wtforms.fields import SelectFieldBase
from wtforms.validators import ValidationError


__all__ = (
    'ModelSelectField', 'QuerySetSelectField',
)


class QuerySetSelectField(SelectFieldBase):
    """
    Given a QuerySet either at initialization or inside a view, will display a
    select drop-down field of choices. The `data` property actually will
    store/keep an ORM model instance, not the ID. Submitting a choice which is
    not in the queryset will result in a validation error. 

    Specifying `label_attr` in the constructor will use that property of the
    model instance for display in the list, else the model object's `__str__`
    or `__unicode__` will be used.

    If `allow_blank` is set to `True`, then a blank choice will be added to the
    top of the list. Selecting this choice will result in the `data` property
    being `None`.  The label for the blank choice can be set by specifying the
    `blank_text` parameter.
    """
    widget = widgets.Select()

    def __init__(self, label=u'', validators=None, queryset=None, label_attr='', allow_blank=False, blank_text=u'', **kwargs):
        super(QuerySetSelectField, self).__init__(label, validators, **kwargs)
        self.label_attr = label_attr
        self.allow_blank = allow_blank
        self.blank_text = blank_text
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

    def iter_choices(self):
        if self.allow_blank:
            yield (u'__None', self.blank_text, self.data is None)

        for obj in self.queryset:
            label = self.label_attr and getattr(obj, self.label_attr) or obj
            yield (obj.pk, label, obj == self.data)

    def process_formdata(self, valuelist):
        if valuelist:
            if valuelist[0] == '__None':
                self.data = None
            else:
                self._data = None
                self._formdata = int(valuelist[0])

    def pre_validate(self, form):
        if not self.allow_blank or self.data is not None:
            for obj in self.queryset:
                if self.data == obj:
                    break
            else:
                raise ValidationError(self.gettext('Not a valid choice'))


class ModelSelectField(QuerySetSelectField):
    """
    Like a QuerySetSelectField, except takes a model class instead of a
    queryset and lists everything in it.
    """
    def __init__(self, label=u'', validators=None, model=None, **kwargs):
        super(ModelSelectField, self).__init__(label, validators, queryset=model._default_manager.all(), **kwargs)
