#!/usr/bin/python
"""
    runtests
    ~~~~~~~~
    
    Runs all unittests.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""

TESTS = ['test_fields', 'test_validators']


from unittest import defaultTestLoader, TextTestRunner, TestSuite
import sys

suite = TestSuite()
suite.addTest(defaultTestLoader.loadTestsFromNames(TESTS))

runner = TextTestRunner(verbosity=(sys.argv.count('-v') + 1))
runner.run(suite)
