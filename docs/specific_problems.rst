.. _specific_problems:

Solving Specific Problems
=========================

What follows is a collection of recipes that will help you tackle specific
challenges that may crop up when using WTForms along with various other python
frameworks.


Prelude: Poke it with a Stick!
------------------------------

The aim of WTForms is not to do it all, but rather to stick to the basics,
while being compatible with as many frameworks as possible. We attempt to place
useful things in the API so that developers can get what they want out of it,
if the default behaviour is not desired.

For example, many fields in WTForms are iterable to allow you to access
enclosed fields inside them, providing you another way to customize their
rendering. Many attributes on the fields are readily available for you to use
in your templates. We encourage you to use the introspection abilities of the
python interpreter to find new ways to manipulate fields. When introspection
fails, you should try reading the source for insight into how things work and
how you can use things to your advantage.

If you come up with a solution that you feel is useful to others and wish to
share it, please let us know via email or the mailing list, and we'll add it
to this document.


Removing Fields Per-instance
----------------------------

Sometimes, you create a form which has fields that aren't useful in all
circumstances or to all users. While it is indeed possible with form
inheritance to define a form with exactly the fields you need, sometimes it is
necessary to just tweak an existing form. Luckily, forms can have fields removed
post-instantiation by using the ``del`` keyword:

.. code-block:: python

    class MagazineIssueForm(Form):
        title  = TextField()
        year   = IntegerField('Year')
        month  = SelectField(choices=MONTHS)

    def edit_issue():
        publication = get_something_from_db()
        form = MagazineIssueForm(...)

        if publication.frequency == 'annual':
            del form.month

        # render our form

Removing a field from a form will cause it to not be validated, and it will not
show up when iterating the form. It's as if the field was never defined to
begin with.  Note that you cannot add fields in this way, as all fields must
exist on the form when processing input data.


Dynamic Form Composition
------------------------

This is a rare occurrence, but sometimes it's necessary to create or modify a
form dynamically in your view. This is possible by creating internal
subclasses:

.. code-block:: python

    def my_view():
        class F(MyBaseForm):
            pass

        F.username = TextField('username')
        for name in iterate_some_model_dynamically():
            setattr(F, name, TextField(name.title())) 

        form = F(request.POST, ...)
        # do view stuff

For more form composition tricks, refer to `this mailing list post`_

.. _this mailing list post: http://groups.google.com/group/wtforms/browse_thread/thread/7099776aacd989e0/772807dfb4b9635b?#772807dfb4b9635b


Rendering Errors
----------------

In your template, you will often find yourself faced with the repetitive task
of rendering errors for a form field. Here's a Jinja2_ macro that may save you time:

.. code-block:: html+jinja

    {% macro with_errors(field) %}
        <div class="form_field">
        {% if field.errors %}
            {% set css_class = 'has_error ' + kwargs.pop('class', '') %}
            {{ field(class=css_class, **kwargs) }}
            <ul class="errors">{% for error in errors %}<li>{{ error|e }}</li>{% endfor %}</ul>
        {% else %}
            {{ field(**kwargs) }}
        {% endif %}
        </div>
    {% endmacro %}

    Usage: {{ with_errors(form.field, style='font-weight: bold') }}

.. _Jinja2: http://jinja.pocoo.org/2/


Specialty Field Tricks
----------------------

By using widget and field combinations, it is possible to create new
behaviours and entirely new ways of displaying a form input to the user.

A classic example is easily supported using the `widget=` keyword arg, such as
making a hidden field which stores and coerces integer data::

    user_id = IntegerField(widget=HiddenInput())

Alternatively, you can create a field which does this by subclassing::

    class HiddenInteger(IntegerField):
        widget = HiddenInput()

Some fields support even more sophisticated customization.For example, what if
a multiple-select was desired where instead of using a multi-row ``<select>``,
a series of checkboxes was used? By using widgets, one can get that behavior
very easily::

    class MultiCheckboxField(SelectMultipleField):
        """
        A multiple-select, except displays a list of checkboxes.

        Iterating the field will produce subfields, allowing custom rendering of
        the enclosed checkbox fields.
        """
        widget = widgets.ListWidget(prefix_label=False)
        option_widget = widgets.CheckboxInput()

By overriding `option_widget`, our new multiple-select when iterated will now
produce fields that render as checkboxes.
