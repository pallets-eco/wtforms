Widgets
=======
.. module:: wtforms.widgets

Widgets are classes whose purpose are to render a field to its usable
representation, usually XHTML.  When a field is called, the default behaviour
is to delegate the rendering to its widget. This abstraction is provided so
that widgets can easily be created to customize the rendering of existing
fields.

.. autoclass:: Widget
    
    .. automethod:: render

Built-in widgets
----------------

.. autoclass:: ListWidget
.. autoclass:: TableWidget
.. autoclass:: Input
.. autoclass:: TextInput
.. autoclass:: HiddenInput 
.. autoclass:: CheckboxInput
.. autoclass:: FileInput
.. autoclass:: SubmitInput
.. autoclass:: TextArea
.. autoclass:: Select 

Custom widgets
--------------

Widgets, much like validators, provide a simple callable contract. Widgets can
take customization arguments through their constructor if needed as well. When
the field is called or printed, it will call the widget with itself as the
first argument and then any additional arguments passed to its caller as
keywords.  Passing the field is done so that one instance of a widget might be
used across many field instances.

Let's look at a sample widget that does something rad::

    class RadTextWidget(Widget):
        def __init__(self, omg):
            pass # TODO
