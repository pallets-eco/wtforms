#!/usr/bin/env python
import os
import sys
from unittest import defaultTestLoader, TextTestRunner, TestSuite

TESTS = ('form', 'fields', 'validators', 'widgets', 'webob_wrapper', 'translations', 'ext_csrf', 'ext_i18n')

def make_suite(prefix='', extra=()):
    tests = TESTS + extra
    test_names = list(prefix + x for x in tests)
    suite = TestSuite()
    suite.addTest(defaultTestLoader.loadTestsFromNames(test_names))
    return suite

def additional_tests():
    """
    This is called automatically by setup.py test
    """
    return make_suite('tests.')

def main():
    extra_tests = tuple(x for x in sys.argv[1:] if '-' not in x)
    suite = make_suite('', extra_tests)

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    runner = TextTestRunner(verbosity=(sys.argv.count('-v') - sys.argv.count('-q') + 1))
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())

if __name__ == '__main__':
    main()
