class Meta
==========

.. module:: wtforms.meta

the `class Meta` paradigm allows WTForms features to be customized, and even
new behaviors to be introduced. It also supplies a place where configuration
for any complementary modules can be done.

For the majority of users, using a class Meta is mostly going to be done for
customizing options used by the default behaviors, however for completeness
the entire API of the `Meta` interface is shown here.


.. autoclass:: DefaultMeta
    
    **Configuration**
    
    .. attribute:: csrf

        Setting `csrf` to True will enable CSRF for the form. The value can 
        also be overridden per-instance by providing ``csrf=True/False`` to
        the constructor of Form.

    .. attribute:: csrf_class

        If set, this is a class which is used to implement CSRF protection.
        Read the documentation on CSRF to get more information


    .. attribute:: csrf_field_name

        The name of the automatically added CSRF token field. Defaults to 
        ``csrf_token``.

    .. attribute:: locales

        Setting `locales` to a sequence of strings specifies the priority order
        of locales to try to find translations for built-in messages of WTForms.

    .. attribute:: cache_translations

        If `True` (the default) then cache translation objects. The default 
        cache is done at class-level so it's shared with all class Meta.

    **Advanced Customization**

    Usually, you do not need to override these methods, as they provide core
    behaviors of WTForms.

    .. automethod:: build_csrf

    .. automethod:: get_translations

    .. automethod:: bind_field

    .. automethod:: wrap_formdata