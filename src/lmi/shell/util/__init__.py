from collections import Iterable
from cast import *
from prompt import *
from url import *


def _is_dict(obj):
    # TODO: wbem.NocaseDict ?
    return isinstance(obj, dict)


def _is_iterable(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, basestring)


def _is_true(obj):
    if isinstance(obj, tuple):
        return bool(obj[1])
    return bool(obj)


def _iter_obj(obj):
    if _is_dict(obj):
        return obj.itervalues()
    return iter(obj)


def is_predicate(obj, predicate):
    '''
    Returns True, if all members (recursive) satisfy the predicate.
    '''
    if callable(predicate) is False:
        raise TypeError('predicate must be callable')

    if _is_iterable(obj):
        for elem in _iter_obj(obj):
            if not is_predicate(elem, predicate):
                return False
        return True

    return predicate(obj)


def is_none(*args):
    '''
    Returns True if obj is None, or all the elements of obj are None.
    '''
    return is_predicate(args, lambda x: x is None)


def is_negative(*args):
    '''
    Return True if obj is negative, or all the elements of obj are negative.
    '''
    return is_predicate(args, lambda x: not x)


def flatten(d):
    '''
    Returns a dict covnerted into a tuple.
    '''
    def flatten_dict(d):
        return d.items()

    def flatten_list(l):
        return tuple(l)

    if isinstance(d, dict):
        return flatten(flatten_dict(d))
    elif isinstance(d, list):
        return flatten(flatten_list(d))
    elif isinstance(d, tuple):
        return tuple(flatten(m) for m in d)
    else:
        return d


def generator_first(g, default=None, delete=True):
    '''
    Returns a first element from generator.  If such generator generates an
    empty sequence, default is returned instead.  The generator object is
    deleted before returning the first element.
    '''
    try:
        rval = g.next()
        if delete:
            del g
        return rval
    except StopIteration:
        return default


# TODO: remove?
#def nowsman(func):
#    '''
#    Used for methods, which are CIM-XML exclusive.
#    '''
#    from functools import wraps
#    from lmi.shell.logger import logger

#    def get_self(*args):
#        return args[0]

#    @wraps(func)
#    def wrapped(*args, **kwargs):
#        self = get_self(*args)
#        if self.conn.is_wsman():
#            # WSMAN client doesn't support this type of call.
#            logger.info("WSMAN client doesn't support this type of call")
#            logger.info(func.__name__)
#            return None
#        return func(*args, **kwargs)
#    return wrapped
