from __future__ import unicode_literals

from unittest import TestCase
from wtforms.ext.i18n.utils import get_translations

class I18NTest(TestCase):
    def test_failure(self):
        self.assertRaises(IOError, get_translations, [])

    def test_us_translation(self):
        translations = get_translations(['en_US'])
        self.assertEqual(translations.gettext('Invalid Mac address.'), 'Invalid MAC address.')


if __name__ == '__main__':
    from unittest import main
    main()

