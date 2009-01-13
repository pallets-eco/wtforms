Forms
=====
.. module:: wtforms.form

Forms provide the highest level API in WTForms. They contain your field
definitions, delegate validation, take input, aggregate errors, and in
general function as the glue holding everything together.

.. autoclass:: Form
    :members:

    **Properties**

    .. attribute:: errors

        A dict, containing field names on this form as keys, with the value
        portion being the list of errors for that field.  The dict is empty
        until after :meth:`validate` is called.

    .. attribute:: data
        
        A dict that is generated on the fly which contains field names as keys
        mapped to the `.data` attribute of the field.

    **Methods**

    .. automethod:: validate

        Runs validation on each field in the form, collecting any errors.
        Returns `True` if no errors occur.  

        For each field, the validators are called in this order:

        1. Any validators passed via a list to the field's constructor.
        2. The field's built-in validation.
        3. Any inline validator for the field defined on the form itself.

        If any of the validators in the chain raises a
        :class:`~wtforms.validators.StopValidation`, then the validation chain
        for that field is stopped.

    .. automethod:: auto_populate

        One common usage of this is an edit profile view::
            
            def edit_profile(request):
                user = User.objects.get(pk=request.session['userid'])
                form = EditProfileForm(request.POST, obj=user)

                if request.POST and form.validate():
                    form.auto_populate(user)
                    user.save()
                    return redirect('/home')
                return render_to_response('edit_profile.html', form=form)

        In the above example, because the form isn't directly tied to the user
        object, you don't have to worry about any dirty data getting onto there
        until you're ready to move it over.

    .. automethod:: __iter__

        Iterate form fields in their order of definition on the form.  Useful 
        for generating forms in templates:

        .. code-block:: django

            {% for field in form %}
                <tr>
                    <th>{{ field.label }}</th>
                    <td>{{ field }}</td>
                </tr>
            {% endfor %}

    .. automethod:: __contains__
        
        Returns :const:`True` if the named field is a member of this form.

Defining forms
--------------

To define a form, one makes a subclass of :class:`Form` and defines the fields
declaratively as class attributes::

    class MyForm(Form):
        first_name = TextField(u'First Name', validators=[validators.required()])
        last_name  = TextField(u'Last Name', validators=[validators.optional()])

Field names can be any valid python identifier, with the following restrictions:
    
* Field names are case-sensitive.
* Field names may not begin with "_" (underscore)
* Field names may not begin with "validate"

Form Inheritance
~~~~~~~~~~~~~~~~

Forms may subclass other forms as needed.  The new form will contain all fields
of the parent form, as well as any new fields defined on the subclass.  A field
name re-used on a subclass causes the new definition to obscure the original.

.. code-block:: python

    class PastebinEdit(Form):
        language = SelectField(u'Programming Language', choices=PASTEBIN_LANGUAGES)
        code     = TextAreaField()

    class PastebinEntry(PastebinEdit):
        name = TextField(u'User Name')   


In-line validators
~~~~~~~~~~~~~~~~~~

In order to provide custom validation for a single field without needing to
write a one-time-use validator, validation can be defined inline by defining a
method with the convention `validate_fieldname`::

    class SignupForm(Form):
        age = IntegerField(u'Age')

        def validate_age(form, field):
            if field.data < 13:
                raise ValidationError("We're sorry, you must be 13 or older to register")

Using forms
-----------

A form is most often constructed in the controller code for handling an action,
with the form data wrapper from the framework passed to its constructor, and
optionally an ORM object.  The constructed form can then validate any input
data and generate errors if invalid.  The form object can then be passed along
to template code to render the form fields along with any errors which
occurred.
