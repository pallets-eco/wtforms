Forms
=====
.. module:: wtforms.form

Forms provide the highest level API in WTForms. They contain your field
definitions, delegate validation, take input, aggregate errors, and in
general function as the glue holding everything together.

The Form base class
-------------------

.. autoclass:: Form

    **Properties**

    .. attribute:: data

        A dict containing the data for each field.
        
        Note that this is generated each time you access the property, so care
        should be taken when using it, as it can potentially be very expensive
        if you repeatedly access it. Typically used if you need to iterate all
        data in the form. If you just need to access the data for known fields,
        you should use `form.<field>.data`, not this proxy property.

    .. attribute:: errors

        A dict containing a list of errors for each field. Empty if the form
        hasn't been validated, or there were no errors.
        
        Note that this is a lazy property, and will only be generated when you
        first access it. If you call :meth:`validate` after accessing it, the
        cached result will be invalidated and regenerated on next access.

    **Methods**

    .. automethod:: validate

    .. automethod:: populate_obj

        One common usage of this is an edit profile view::
            
            def edit_profile(request):
                user = User.objects.get(pk=request.session['userid'])
                form = EditProfileForm(request.POST, obj=user)

                if request.POST and form.validate():
                    form.populate_obj(user)
                    user.save()
                    return redirect('/home')
                return render_to_response('edit_profile.html', form=form)

        In the above example, because the form isn't directly tied to the user
        object, you don't have to worry about any dirty data getting onto there
        until you're ready to move it over.

    .. automethod:: __iter__

        .. code-block:: django

            {% for field in form %}
                <tr>
                    <th>{{ field.label }}</th>
                    <td>{{ field }}</td>
                </tr>
            {% endfor %}

    .. automethod:: __contains__

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
