#!/usr/bin/env python
import os
import sys
from unittest import defaultTestLoader, TextTestRunner, TestSuite

TESTS = ('form', 'fields', 'validators', 'widgets', 'webob_wrapper', 'translations', 'ext_csrf', 'i18n')

OPTIONAL_TESTS = ('ext_django.tests', 'ext_sqlalchemy', 'ext_dateutil', 'locale_babel')


def make_suite(prefix='', extra=()):
    tests = TESTS + extra
    test_names = list(prefix + x for x in tests)
    suite = TestSuite()
    suite.addTest(defaultTestLoader.loadTestsFromNames(test_names))
    for name in OPTIONAL_TESTS:
        test_name = prefix + name
        try:
            suite.addTest(defaultTestLoader.loadTestsFromName(test_name))
        except (ImportError, AttributeError):
            sys.stderr.write("### Disabled test '%s', dependency not found\n" % name)
    return suite


def additional_tests():
    """
    This is called automatically by setup.py test
    """
    return make_suite('tests.')


def main():
    my_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(my_dir, '..')))
    has_pep8 = False
    try:
        import pep8
        has_pep8 = True
    except ImportError:
        if '--with-pep8' in sys.argv[1:]:
            sys.stderr.write('# Could not find pep8 library.')
            sys.exit(1)

    if has_pep8:
        guide = pep8.StyleGuide(
            ignore=[],
            paths=['wtforms/'],
            exclude=[],
            max_line_length=130,
        )
        report = guide.check_files()
        if report.total_errors:
            sys.exit(1)

    extra_tests = tuple(x for x in sys.argv[1:] if '-' not in x)
    suite = make_suite('', extra_tests)

    runner = TextTestRunner(verbosity=(sys.argv.count('-v') - sys.argv.count('-q') + 1))
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())

if __name__ == '__main__':
    main()
