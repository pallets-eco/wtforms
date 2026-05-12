"""Compatibility helpers for different Python versions."""

import inspect
import sys

if sys.version_info >= (3, 14):
    from annotationlib import Format

    def get_signature(callable):
        return inspect.signature(callable, annotation_format=Format.FORWARDREF)

else:

    def get_signature(callable):
        return inspect.signature(callable)
