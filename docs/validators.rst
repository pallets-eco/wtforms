Validators
==========
.. module:: wtforms.validators

A validator simply takes an input, verifies it fulfills some criterion, such as
a maximum length for a string and returns. Or, if the validation fails, raises
a :class:`~wtforms.validators.ValidationError`. This system is very simple and
flexible, and allows you to chain any number of validators on fields.

.. autoclass:: wtforms.validators.ValidationError
.. autoclass:: wtforms.validators.StopValidation

Built-in validators
-------------------

.. autoclass:: wtforms.validators.Email

.. autoclass:: wtforms.validators.EqualTo

    This validator can be used to facilitate in one of the most common
    scenarios, the password change form::

        class ChangePassword(Form):
            password = PasswordField('New Password', [Required(), EqualTo('confirm', mesage='Passwords must match')])
            confirm  = PasswordField('Repeat Password')

    In the example, we use the Required validator to prevent the EqualTo
    validator from trying to see if the passwords do not match if there was no
    passwords specified at all. Because Required stops the validation chain,
    EqualTo is not run in the case the password field is left empty.

.. autoclass:: wtforms.validators.IPAddress

.. autoclass:: wtforms.validators.Length

.. autoclass:: wtforms.validators.NumberRange

.. autoclass:: wtforms.validators.Optional

   This also sets the ``optional`` :attr:`flag <wtforms.fields.Field.flags>` on
   fields it is used on.

.. autoclass:: wtforms.validators.Required

   This also sets the ``required`` :attr:`flag <wtforms.fields.Field.flags>` on
   fields it is used on.

.. autoclass:: wtforms.validators.Regexp

.. autoclass:: wtforms.validators.URL

Custom validators
-----------------

We will step through the evolution of writing a length-checking validator
similar to the built-in :class:`Length` validator, starting from a
case-specific one to a generic reusable validator.

Let's start with a simple form with a name field and its validation::

    class MyForm(Form):
        name = TextField('Name', [Required()])

        def validate_name(form, field):
            if len(field.data) > 50:
                raise ValidationError('Name must be less than 50 characters')

Above, we show the use of an :ref:`in-line validator <inline-validators>` to do
validation of a single field. In-line validators are good for validating
special cases, but are not easily reusable.  If, in the example above, the
`name` field were to be split into two fields for first name and surname, you
would have to duplicate your work to check two lengths.

So let's start on the process of splitting the validator out for re-use::

    def my_length_check(form, field):
        if len(field.data) > 50:
            raise ValidationError('Field must be less than 50 characters')

    class MyForm(Form):
        name = TextField('Name', [Required(), my_length_check])

All we've done here is move the exact same code out of the class and as a
function. Since a validator can be any callable which accepts the two
positional arguments form and field, this is perfectly fine, but the validator
is very special-cased.

Instead, we can turn our validator into a more powerful one by making it a
factory which returns a callable::

    def length(min=-1, max=-1):
        message = 'Must be between %d and %d characters long.' % (min, max)

        def _length(form, field):
            l = field.data and len(field.data) or 0
            if l < min or max != -1 and l > max:
                raise ValidationError(message)

        return _length

    class MyForm(Form):
        name = TextField('Name', [Required(), length(max=50)])

Now we have a configurable length-checking validator that handles both minimum
and maximum lengths. When ``length(max=50)`` is passed in your validators list,
it returns the enclosed `_length` function as a closure, which is used in the
field's validation chain.

This is now an acceptable validator, but we recommend that for reusability, you
use the pattern of allowing the error message to be customized via passing a
``message=`` parameter:

.. code-block:: python

    class Length(object):
        def __init__(self, min=-1, max=-1, message=None):
            self.min = min
            self.max = max
            if not message:
                message = u'Field must be between %i and %i characters long.' % (min, max)
            self.message = message

        def __call__(self, form, field):
            l = field.data and len(field.data) or 0
            if l < self.min or self.max != -1 and l > self.max:
                raise ValidationError(self.message)

    length = Length

In addition to allowing the error message to be customized, we've now converted
the length validator to a class. This wasn't necessary, but we did this to
illustrate how one would do so. Because fields will accept any callable as a
validator, callable classes are just as applicable. For complex validators, or
using inheritance, you may prefer this.

We aliased the ``Length`` class back to the original ``length`` name in the
above example. This allows you to keep API compatibility as you move your
validators from factories to classes, and thus we recommend this for those
writing validators they will share.


Setting flags on the field with validators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes, it's useful to know if a validator is present on a given field, like
for use in template code. To do this, validators are allowed to specify flags
which will then be available on the :attr:`field's flags object
<wtforms.fields.Field.flags>`.  Some of the built-in validators such as
:class:`Required` already do this.

To specify flags on your validator, set the ``field_flags`` attribute on your
validator. When the Field is constructed, the flags with the same name will be
set to True on your field. For example, let's imagine a validator that
validates that input is valid BBCode. We can set a flag on the field then to
signify that the field accepts BBCode::

    # class implementation
    class ValidBBCode(object):
        field_flags = ('accepts_bbcode', )

        pass # validator implementation here

    # factory implementation
    def valid_bbcode():
        def _valid_bbcode(form, field):
            pass # validator implementation here

        _valid_bbcode.field_flags = ('accepts_bbcode', )
        return _valid_bbcode

Then we can check it in our template, so we can then place a note to the user:

.. code-block:: html+jinja

    {{ field(rows=7, cols=70) }}
    {% if field.flags.accepts_bbcode %}
        <div class="note">This field accepts BBCode formatting as input.</div>
    {% endif %}

Some considerations on using flags:

* Flags can only set boolean values, and another validator cannot unset them.
* If multiple fields set the same flag, its value is still True.
* Flags are set from validators only in :meth:`Field.__init__`, so inline
  validators and extra passed-in validators cannot set them.
