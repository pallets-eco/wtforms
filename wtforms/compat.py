import sys

if sys.version_info[0] >= 3:
    text_type = str
    string_types = str
    iteritems = lambda o: o.items()
    izip = zip
    exec_ = eval("exec")

    def with_metaclass(meta, base=object):
        ns = dict(base=base, meta=meta)
        exec_("""class NewBase(base, metaclass=meta):
    pass""", ns)
        return ns["NewBase"]
else:
    text_type = unicode
    string_types = basestring
    iteritems = lambda o: o.iteritems()
    from itertools import izip

    def with_metaclass(meta, base=object):
        class NewBase(base):
            __metaclass__ = meta
        return NewBase

