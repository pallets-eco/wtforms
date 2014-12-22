from wtforms import Form, TextField
from werkzeug.datastructures import MultiDict

class TestForm(Form):
    field_a = TextField('first')
    field_b = TextField('second')

class Dummy():
    field_a = 'apple'
    field_b = 'banana'

class DummyPostData(dict):
    def getlist(self, key):
        v = self[key]
        if not isinstance(v, (list, tuple)):
            v = [v]
        return v


if __name__ == "__main__":
    d = Dummy()
    print d.field_a, d.field_b
    # purposely only include 1 of the 2 fields
    #formdata = DummyPostData({'field_a': 'cat'})
    formdata = MultiDict({'field_a': 'cat'})
    #f = TestForm(formdata=None, field_b='toast')
    f = TestForm(formdata, d)
    print f.validate()
    # now we should retain our current value instead of stomping it
    f.populate_obj(d, partial=True)
    print d.field_a, d.field_b
