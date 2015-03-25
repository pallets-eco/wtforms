#!/usr/bin/env python
import os
import sys
from unittest import defaultTestLoader, TextTestRunner, TestSuite

TESTS = ('form', 'fields', 'validators', 'widgets', 'webob_wrapper', 'csrf', 'ext_csrf', 'i18n')

OPTIONAL_TESTS = ('ext_django.tests', 'ext_sqlalchemy', 'ext_dateutil', 'locale_babel')


def make_suite(prefix='', extra=(), force_all=False):
    tests = TESTS + extra
    test_names = list(prefix + x for x in tests)
    suite = TestSuite()
    suite.addTest(defaultTestLoader.loadTestsFromNames(test_names))
    for name in OPTIONAL_TESTS:
        test_name = prefix + name
        try:
            suite.addTest(defaultTestLoader.loadTestsFromName(test_name))
        except (ImportError, AttributeError):
            if force_all:
                # If force_all, don't let us skip tests
                raise ImportError('Could not load test module %s and force_all is enabled.' % test_name)
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

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--with-pep8', action='store_true', dest='with_pep8', default=False)
    parser.add_option('--force-all', action='store_true', dest='force_all', default=False)
    parser.add_option('-v', '--verbose', action='count', dest='verbosity', default=0)
    parser.add_option('-q', '--quiet', action='count', dest='quietness', default=0)
    options, extra_args = parser.parse_args()
    has_pep8 = False
    try:
        import pep8
        has_pep8 = True
    except ImportError:
        if options.with_pep8:
            sys.stderr.write('# Could not find pep8 library.')
            sys.exit(1)

    if has_pep8:
        guide_main = pep8.StyleGuide(
            ignore=[],
            paths=['wtforms/'],
            exclude=[],
            max_line_length=130,
        )
        guide_tests = pep8.StyleGuide(
            ignore=['E221', 'E731', 'E402'],
            paths=['tests/'],
            max_line_length=150,
        )
        for guide in (guide_main, guide_tests):
            report = guide.check_files()
            if report.total_errors:
                sys.exit(1)

    suite = make_suite('', tuple(extra_args), options.force_all)

    runner = TextTestRunner(verbosity=options.verbosity - options.quietness + 1)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())

if __name__ == '__main__':
    main()
