#!/usr/bin/env python
"""
    widgets
    ~~~~~~~
    
    Unittests for widgets.
"""
from unittest import TestCase
from wtforms.widgets import html_params


class TestHTMLParams(TestCase):
    def test(self):
        self.assertEqual(html_params(foo=9, k='wuuu'), u'foo="9" k="wuuu"')
        self.assertEqual(html_params(class_='foo'), u'class="foo"')
        self.assertEqual(html_params(class__='foo'), u'class_="foo"')


if __name__ == '__main__':
    from unittest import main
    main()
