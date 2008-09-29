Validators
==========
.. module:: wtforms.validators

Validators simply takes an input, verifies it fulfills some criterion, such as
a maximum length for a string and returns. Or, if the validation fails, raises
a :class:`~wtforms.validators.ValidationError`. This system is very simple and
flexible, and allows you to chain any number of validators on fields.

.. autoclass:: wtforms.validators.ValidationError

Built-in validators
===================

.. autofunction:: wtforms.validators.email
.. autofunction:: wtforms.validators.equal_to
.. autofunction:: wtforms.validators.ip_address
.. autofunction:: wtforms.validators.is_checked
.. autofunction:: wtforms.validators.length
.. autofunction:: wtforms.validators.not_empty
.. autofunction:: wtforms.validators.regexp
.. autofunction:: wtforms.validators.url

Custom validators
=================

Defining your own validators is easy. You simply make a function that takes a
list of configuration directives, and then returns a callable. The validator
should always accept the `message` argument to provide a way to override the
error message.

Let's look at one of the built-in validators, not_empty::

    def not_empty(message=u'Field must not be empty.'):
        def _not_empty(form, field):
            if not field.data or not field.data.strip():
                raise ValidationError(message)
        return _not_empty

And the way it's used::

    password = PasswordField(u'Password', [validators.not_empty(u'Please provide a password.')])

The outer function sets configuration directives, in this case just the
message. The inner function provides the actual validation: If the field
contains no data, or only contains whitespace, a :class:`~wtforms.validators.ValidationError`
with the message is raised. Otherwise we just the let function return normally.

You could also define the validator as a class::

    class NotEmpty(object):
        def __init__(self, message=u'Field must not be empty.'):
            self.message = message

        def __call__(self, form, field):
            if not field.data or not field.data.strip():
                raise ValidationError(self.message)

Which option you choose is entirely down to preference.
