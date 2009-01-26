Validators
==========
.. module:: wtforms.validators

A validator simply takes an input, verifies it fulfills some criterion, such as
a maximum length for a string and returns. Or, if the validation fails, raises
a :class:`~wtforms.validators.ValidationError`. This system is very simple and
flexible, and allows you to chain any number of validators on fields.

.. autoclass:: wtforms.validators.Validator
.. autoclass:: wtforms.validators.ValidationError
.. autoclass:: wtforms.validators.StopValidation

Built-in validators
-------------------

.. autoclass:: wtforms.validators.Email
.. autoclass:: wtforms.validators.EqualTo
.. autoclass:: wtforms.validators.IPAddress
.. autoclass:: wtforms.validators.Length
.. autoclass:: wtforms.validators.Optional
.. autoclass:: wtforms.validators.Required
.. autoclass:: wtforms.validators.Regexp
.. autoclass:: wtforms.validators.URL

Custom validators
-----------------

Defining your own validators is easy. You simply make a function that takes a
list of configuration directives, and then returns a callable. The returned
callable should take two positional arguments, which are a form instance and
the field instance being validated. It is helpful to design your validators
with a `message` argument to provide a way to override the error message.

Let's look at a possible validator which checks if a file upload's extension is
that of an image::

    def is_image(message=u'Images only!', extensions=None):
        if not extensions:
            extensions = ('jpg', 'jpeg', 'png', 'gif')
        def _is_image(form, field):
            if not field.data or field.data.split('.')[-1] not in extensions:
                raise ValidationError(message)
        return _is_image

And the way it's used::

    avatar = FileField(u'Avatar', [is_image(u'Only images are allowed.', extensions=['gif', 'png'])])

The outer function sets configuration directives, in this case the message and
the extensions. The inner function provides the actual validation: If the
field contains no data, or an un-approved extension,
:class:`~wtforms.validators.ValidationError` with the message is raised.
Otherwise we just the let function return normally.

You could also define the validator as a class::

    class IsImage(object):
        def __init__(self, message=u'Images only!', extensions=None):
            self.message = message
            if not extensions:
                extensions = ('jpg', 'jpeg', 'png', 'gif')
            self.extensions = extensions

        def __call__(self, form, field):
            if not field.data or field.data.split('.')[-1] not in extensions:
                raise ValidationError(self.message)

Which option you choose is entirely down to preference.
