import warnings
import unittest

from wtforms.widgets import HTMLString, escape_html
import markupsafe


class TestDeprecation(unittest.TestCase):
    def test_htmlstring(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(markupsafe.Markup("foobar"), HTMLString("foobar"))
            self.assertEqual(len(w), 1)
            assert issubclass(w[-1].category, DeprecationWarning)

    def test_escape(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(markupsafe.escape("foobar"), escape_html("foobar"))
            self.assertEqual(len(w), 1)
            assert issubclass(w[-1].category, DeprecationWarning)
