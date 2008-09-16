Crash Course
============

currently in progress.

Getting Started
---------------

If you have easy_install set up, you can simply execute *easy_install WTForms* 
to get it installed.  Otherwise, you can get it from 
`PyPI <http://pypi.python.org/pypi/WTForms/>` and install it with *setup.py install*.

Once you've done that, you can begin writing your first Form::

    from wtforms import Form, BooleanField, TextField, PasswordField, validators

    class RegistrationForm(Form):
        username     = TextField('Username', validators.length(min=4, max=25))
        email        = TextField('Email Address', validators.length(min=6, max=35))
        accept_rules = BooleanField('I accept the site rules')


Using it in a view
------------------

::

    def register(request):
        form = RegistrationForm(request.POST, prefix='register')
        if request.POST and form.validate():
            # create new user and show the confirmation page
            pass
        return render_to_response('account/register', {'form': form})
    

Rendering your form in templates
--------------------------------

.. code-block:: jinja

    <form method="post" action="/register">
    <table>
      <tr>
        <th>{{ form.username.label }}</th>
        <td>{{ form.username }}</td>
      </tr>
      <tr>
        <th>{{ form.email.label }}</th>
        <td>{{ form.email }}</td>
      </tr>
      <tr>
        <td></td>
        <td>{{ form.accept_rules }} {{ form.accept_rules.label }}</td>
    </table>
    <input type="submit" value="Register!" />
    </form>

If you inspect the above carefully, you will notice a few things.  While wtforms will 
generate input fields, it will not generate the <form> tags.  It can be made to 
generate submit buttons if you feel the need to check for submit button inputs 
(more about that in the future) but you're not forced to.

Field customization in Jinja templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to add customization to your form fields (such as CSS 
classes, onclick events, etc) you can do so by passing keyword 
args to the form fields as such:

.. code-block:: jinja

  {{ form.username(class="big_text", onclick="do_something()") }}


Field customization in Django templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adding :mod:`wtforms.ext.django` to your INSTALLED_APPS will make the wtforms 
template library available to your application.  With this you can pass extra 
attributes to form fields similar to the usage in jinja:

.. code-block:: django

  {% load wtforms %}

  {% form_field form.username class="big_text" onclick="do_something()" %}


**Note** if you're using the newest development version of Django, output from 
wtforms using the `{{ form.field }}` syntax will be auto-escaped.  
To avoid this happening, use the Django's `{% autoescape off %}` block tag or 
use WTForms' `form_field` template tag.


Adding custom validation
------------------------

In the example above, you can see we are using some of the built-in validators 
from the :mod:`wtforms.validators` module. You can also define your own validators 
like so::

    from wtforms.validators import ValidationError
    import re

    def validate_telephone(form, field):
        if not re.match(r'([0-9]{3,4}-?)+', field.data):
            raise ValidationError(u'This does not look like a valid telephone number to me. Try dash-separated triads.')


A validator is just a python callable which takes two arguments. It could 
just as easily be a class or a function closure if you want.

Since one-time use validators are likely to be used often, we have 
developed a way to write them inline::

    class RegistrationForm(Form):
        username         = TextField('Username', validators.length(min=4, max=25))
        
        def _validate_username(form, field):
            if not re.match(r'[a-z][A-Z0-9_-]+', field.data, re.I):
                raise ValidationError(u'Usernames must start with a letter and consist only of letters, numbers, and - _')



Using select fields
-------------------

Select fields keep a `choices` property which is a sequence of `(value, label)` 
pairs.  The value portion can be any type in theory, but as form data is sent 
as strings, you will need to provide a function which can coerce the string 
representation back to a comparable object.  More about this later.


Select fields with static choice values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    class PastebinEntry(Form):
        language = SelectField(u'Programming Language', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])

Note that the `choices` keyword is only evaluated once, so if you want to make 
a dynamic drop-down list that could change during the runtime of the application, 
you'll want to look at the next section.


Select fields with dynamic choice values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    class UserDetails(Form):
        group_id = SelectField(u'Group', checker=int)
        username = TextField

    def edit_user(request, id):
        user = User.query.get(id)
        form = UserDetails(request.POST, obj=user)
        form.group_id.choices = [(g.id, g.name) for g in Group.query.order_by('name')]

        if request.POST and form.validate():
            # Copy all the form values onto the user object
            form.auto_populate(user) 
            db.session.flush([user])

        return render_to_response('edit_user.html', {'form': form})

Note we didn't pass a `choices=` to the :class:`wtforms.SelectField` constructor, 
but rather created the list in the view function. Also, the `checker=` keyword 
arg to `wtforms.SelectField` says that we use :func:`int()` to coerce form data.  
The default checker is :func:`str`.  '''Note:''' this will be changing to 
:func:`unicode` in future releases.

This code example also highlights another feature of wtforms: having a form's default 
values be that of a model object, and then copying the fields back to the model object 
on save  (Unlike other forms frameworks, we do not directly modify your db model 
object, it is up to you when and if you want this to happen.)
