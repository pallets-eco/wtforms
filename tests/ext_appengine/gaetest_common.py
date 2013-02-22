"""
This contains common tools for gae tests, and also sets up the environment.

It should be the first import in the unit tests.
"""
# -- First setup paths
import sys
import os
my_dir = os.path.dirname(os.path.abspath(__file__))
WTFORMS_DIR = os.path.abspath(os.path.join(my_dir, '..', '..'))
sys.path.insert(0, WTFORMS_DIR)

SAMPLE_AUTHORS = (
    ('Bob', 'Boston'),
    ('Harry', 'Houston'),
    ('Linda', 'London'),
)


class DummyPostData(dict):
    def getlist(self, key):
        v = self[key]
        if not isinstance(v, (list, tuple)):
            v = [v]
        return v


def fill_authors(Author):
    """
    Fill authors from SAMPLE_AUTHORS.
    Model is passed so it can be either an NDB or DB model.
    """
    AGE_BASE = 30
    authors = []
    for name, city in SAMPLE_AUTHORS:
        author = Author(name=name, city=city, age=AGE_BASE)
        author.put()
        authors.append(author)
        AGE_BASE += 1
    return authors
