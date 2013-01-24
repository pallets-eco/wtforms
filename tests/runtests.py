#!/usr/bin/env python
import os
import sys
from unittest import defaultTestLoader, TextTestRunner, TestSuite

TESTS = ('form', 'fields', 'validators', 'widgets', 'webob_wrapper', 'translations', 'ext_csrf', 'ext_i18n')

OPTIONAL_TESTS = ('ext_django.tests', 'ext_sqlalchemy', 'ext_dateutil')

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

    extra_tests = tuple(x for x in sys.argv[1:] if '-' not in x)
    suite = make_suite('', extra_tests)

    runner = TextTestRunner(verbosity=(sys.argv.count('-v') - sys.argv.count('-q') + 1))
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())

if __name__ == '__main__':
    main()
