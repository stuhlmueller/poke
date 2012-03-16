#!/usr/bin/python

import collections

def make_hashable(obj):
    """WARNING: This function only works on a limited subset of objects.
    Make a range of objects hashable."""
    if isinstance(obj, collections.Hashable):
        return obj
    elif isinstance(obj, collections.Iterable):
        return tuple([make_hashable(item) for item in obj])
    else:
        return obj
