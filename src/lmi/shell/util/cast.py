from lmi.shell.core import wbem


def _do_cast(t, value, cast):
    '''
    Helper function, which preforms the actual cast.
    '''
    cast_func = cast.get(t.lower(), lambda x: x)
    if isinstance(value, (dict, wbem.NocaseDict)):
        return wbem.NocaseDict(
            dict((k, _do_cast(t, v, cast)) for k, v in value.iteritems()))
    elif isinstance(value, list):
        return [_do_cast(t, v, cast) for v in value]
    elif isinstance(value, tuple):
        return (_do_cast(t, v, cast) for v in value)
    return cast_func(value) if value is not None else value


def to_cim(t, value):
    '''
    Casts the value to CIM type.
    '''
    cast = {
        'sint8': lambda x: wbem.Sint8(x),
        'uint8': lambda x: wbem.Uint8(x),
        'sint16': lambda x: wbem.Sint16(x),
        'uint16': lambda x: wbem.Uint16(x),
        'sint32': lambda x: wbem.Sint32(x),
        'uint32': lambda x: wbem.Uint32(x),
        'sint64': lambda x: wbem.Sint64(x),
        'uint64': lambda x: wbem.Uint64(x),
        'string': lambda x: unicode(x, 'utf-8') if isinstance(x, str) else x,
        'reference': lambda x: instance_to_path(x)
    }
    return _do_cast(t, value, cast)


def to_lmi(t, value):
    '''
    Casts the value to LMI (python) type.
    '''
    cast = {
        'sint8': lambda x: int(x),
        'uint8': lambda x: int(x),
        'sint16': lambda x: int(x),
        'uint16': lambda x: int(x),
        'sint32': lambda x: int(x),
        'uint32': lambda x: int(x),
        'sint64': lambda x: int(x),
        'uint64': lambda x: int(x),
    }
    return _do_cast(t, value, cast)
