.. _intro:

Introduction
============

So you've cracked your knuckles and started working on that awesome python
webapp you want to write.  Probably it's a blog. Everyone writes a blog as their
first webapp. At some point in time though, your blog goes beyond basic input
and you start thinking about form handling. Enter WTForms.

But why do I need *another* stinking framework? Well, some webapp frameworks
take the approach of associating database models with form handling. While this
can be handy for very basic create/update views, chances are you'll need more
functionality than that. Or maybe you have a generic form handling framework but
you want to customize the HTML generation of those form fields, and define your
own validation. 

With WTForms, your form field HTML can be generated for you, but we let you
customize it in your templates.  This allows you to maintain separation of code
and presentation, and keep those messy parameters out of your python code.
Because we strive for loose coupling, you should be able to do that in any
templating engine you like, as well.  To see examples of how it works, check out
our :ref:`crashcourse`.

