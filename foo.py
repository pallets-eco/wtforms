from wtforms import Form, TextField

class TestForm(Form):
    field_a = TextField('first')
    field_b = TextField('second')

class Dummy():
    field_a = 'apple'
    field_b = 'banana'

if __name__ == "__main__":
    d = Dummy()
    print d.field_a, d.field_b
    # purposely only include 1 of the 2 fields
    data = {'field_a': 'cat'}
    f = TestForm(**data)
    print f.validate()
    print f.field_a.data, f.field_b.data
    # now we should retain our current value instead of stomping it
    f.populate_obj_partial(d)
    print d.field_a, d.field_b
