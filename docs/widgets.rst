Widgets
=======

Widgets are classes whose purpose are to render a field to its usable
representation, usually XHTML.  When a field is called, the default behaviour
is to delegate the rendering to its widget. This abstraction is provided so
that widgets can easily be created to customize the rendering of existing
fields.

**Note** All built-in widgets will return upon rendering a "HTML-safe" unicode
string subclass that many templating frameworks (Jinja, Mako, Genshi) will
recognize as not needing to be auto-escaped.

Built-in widgets
----------------

.. autoclass:: wtforms.widgets.ColorInput
.. autoclass:: wtforms.widgets.Button
.. autoclass:: wtforms.widgets.CheckboxInput
.. autoclass:: wtforms.widgets.DateTimeInput
.. autoclass:: wtforms.widgets.DateTimeLocalInput
.. autoclass:: wtforms.widgets.DateInput
.. autoclass:: wtforms.widgets.EmailInput
.. autoclass:: wtforms.widgets.FileInput
.. autoclass:: wtforms.widgets.HiddenInput
.. autoclass:: wtforms.widgets.Input
.. autoclass:: wtforms.widgets.ListWidget
.. autoclass:: wtforms.widgets.MonthInput
.. autoclass:: wtforms.widgets.NumberInput
.. autoclass:: wtforms.widgets.PasswordInput
.. autoclass:: wtforms.widgets.RadioInput
.. autoclass:: wtforms.widgets.RangeInput
.. autoclass:: wtforms.widgets.SubmitInput
.. autoclass:: wtforms.widgets.SearchInput
.. autoclass:: wtforms.widgets.Select
.. autoclass:: wtforms.widgets.TableWidget
.. autoclass:: wtforms.widgets.TelInput
.. autoclass:: wtforms.widgets.TextArea
.. autoclass:: wtforms.widgets.TextInput
.. autoclass:: wtforms.widgets.TimeInput
.. autoclass:: wtforms.widgets.URLInput
.. autoclass:: wtforms.widgets.WeekInput

Widget-Building Utilities
-------------------------

These utilities are used in WTForms widgets to help render HTML and also in
order to work along with HTML templating frameworks. They can be imported for
use in building custom widgets as well.

.. autofunction:: wtforms.widgets.html_params

WTForms uses `MarkupSafe`_ to escape unsafe HTML characters before
rendering. You can mark a string using :class:`markupsafe.Markup` to
indicate that it should not be escaped.

.. _MarkupSafe: https://markupsafe.palletsprojects.com/


Custom widgets
--------------

Widgets, much like validators, provide a simple callable contract. Widgets can
take customization arguments through a constructor if needed as well. When
the field is called or printed, it will call the widget with itself as the
first argument and then any additional arguments passed to its caller as
keywords.  Passing the field is done so that one instance of a widget might be
used across many field instances.

The widget contract
~~~~~~~~~~~~~~~~~~~

A widget is any callable with the signature ``widget(field, **kwargs)`` that
returns the rendered HTML. The return value should be a
:class:`markupsafe.Markup` instance; otherwise templating engines with
autoescape enabled will escape the markup and the user will see the raw HTML
tags instead of the rendered widget.

Inside the widget, the following ``field`` attributes are commonly used:

- ``field.id`` and ``field.name`` — the rendered ``id``/``name`` attributes.
- ``field.label`` — a :class:`~wtforms.fields.Label` instance, callable to
  render a ``<label>`` tag.
- ``field.errors`` — list of validation errors after ``form.validate()``.
- ``field._value()`` — the string representation of the current value, used
  for the ``value=`` attribute of inputs.
- ``field.iter_choices()`` — for :class:`~wtforms.fields.SelectField` and
  similar; yields :class:`~wtforms.fields.Choice` objects with
  ``value``, ``label``, ``selected`` and ``render_kw``.

To assemble the HTML, use :func:`~wtforms.widgets.html_params` for attribute
strings, :class:`markupsafe.Markup` to mark the result as safe, and
:func:`markupsafe.escape` for any user-supplied content interpolated into the
HTML::

    from markupsafe import Markup, escape
    from wtforms.widgets import html_params

Subclassing a built-in widget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The lightest customization is to extend an existing widget and post-process
its output or its kwargs. Here is a widget that renders a text field with an
extra CSS class when the field has errors::

    class MyTextInput(TextInput):
        def __init__(self, error_class='has_errors'):
            super().__init__()
            self.error_class = error_class

        def __call__(self, field, **kwargs):
            if field.errors:
                existing = kwargs.pop('class', '') or kwargs.pop('class_', '')
                kwargs['class'] = f'{self.error_class} {existing}'.strip()
            return super().__call__(field, **kwargs)

Writing a widget from scratch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A widget does not have to be a class — any callable will do. Here is a widget
that renders a :class:`~wtforms.fields.SelectMultipleField` as a collection of
:mdn-input:`checkbox` controls::

    from markupsafe import Markup, escape
    from wtforms.widgets import html_params

    def select_multi_checkbox(field, ul_class='', **kwargs):
        kwargs.setdefault('type', 'checkbox')
        field_id = kwargs.pop('id', field.id)
        html = [f'<ul {html_params(id=field_id, class_=ul_class)}>']
        for choice in field.iter_choices():
            choice_id = f'{field_id}-{choice.value}'
            options = dict(
                kwargs,
                name=field.name,
                value=choice.value,
                id=choice_id,
                checked=choice._selected,
            )
            html.append(f'<li><input {html_params(**options)}> ')
            html.append(f'<label for="{choice_id}">{escape(choice.label)}</label></li>')
        html.append('</ul>')
        return Markup(''.join(html))

    class TestForm(Form):
        tester = SelectMultipleField(choices=my_choices, widget=select_multi_checkbox)

``widget`` versus ``option_widget``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For fields that wrap a collection of options (such as
:class:`~wtforms.fields.SelectField`, :class:`~wtforms.fields.RadioField` and
their multiple-choice variants), two extension points exist:

- ``widget`` renders the whole field at once (the ``<select>`` element, the
  ``<ul>`` of radios, etc.).
- ``option_widget`` renders a single option when the field is iterated. This
  is useful when you want to keep the default container but change how each
  option is displayed. See :ref:`specific_problems` for an example using
  :class:`~wtforms.widgets.ListWidget` together with
  :class:`~wtforms.widgets.CheckboxInput` as the ``option_widget``.
