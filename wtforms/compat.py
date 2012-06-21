import sys

if sys.version_info[0] >= 3:
    text_type = str
    string_types = str,
    iteritems = lambda o: o.items()
    izip = zip
    exec_ = eval("exec")

else:
    text_type = unicode
    string_types = basestring,
    iteritems = lambda o: o.iteritems()
    from itertools import izip

def with_metaclass(meta, base=object):
    return meta("NewBase", (base,), {})

