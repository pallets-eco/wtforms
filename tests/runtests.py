#!/usr/bin/env python
"""
    runtests
    ~~~~~~~~
    
    Runs all unittests.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""

TESTS = ['form', 'fields', 'validators']


from unittest import defaultTestLoader, TextTestRunner, TestSuite
import sys

suite = TestSuite()
suite.addTest(defaultTestLoader.loadTestsFromNames(TESTS))

runner = TextTestRunner(verbosity=(sys.argv.count('-v') - sys.argv.count('-q') + 1))
result = runner.run(suite)
sys.exit(not result.wasSuccessful())
