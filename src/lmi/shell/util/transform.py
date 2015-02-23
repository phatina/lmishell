import cast
from lmi.shell import obj
from lmi.shell.core import wbem


def to_lmi(conn, value):
    '''
    Transforms returned values from a method call into LMI wrapped objects.
    Returns transformed input, where :py:class:`wbem.CIMInstance` and
    :py:class:`wbem.CIMInstanceName` are wrapped into LMI wrapper classes and
    primitive types are cast to python native types.

    :param LMIConnection conn: connection object
    :param value: object to be transformed into :py:mod:`python` type from
        :mod:`wbem` one
    :returns: transformed py::mod:`wbem` object into LMIShell one
    '''
    if isinstance(value, wbem.CIMInstance):
        namespace = value.path.namespace if value.path else None
        return obj.LMIInstance(conn, value)
    elif isinstance(value, wbem.CIMInstanceName):
        return obj.LMIInstanceName(conn, value)
    elif isinstance(value, wbem.CIMInt):
        return int(value)
    elif isinstance(value, wbem.CIMFloat):
        return float(value)
    elif isinstance(value, (dict, wbem.NocaseDict)):
        return wbem.NocaseDict(
            dict(
                (k, to_lmi(conn, v))
                for k, v in value.iteritems()))
    elif isinstance(value, list):
        return [to_lmi(conn, val) for val in value]
    elif isinstance(value, tuple):
        return (to_lmi(conn, val) for val in value)
    return value


def to_cim_param(t, value):
    '''
    Helper function for method calls, which transforms input object into
    :py:class:`wbem.CIMInstanceName` object. Members if lists, dictionaries and
    tuples are transformed as well. The function does not cast numeric types.

    :param string t: string of CIM type
    :param value: object to be transformed to :py:mod:`wbem` type.
    :returns: transformed LMIShell's object into :py:mod:`wbem` one
    '''
    if isinstance(value, obj.LMIInstance):
        return value.wrapped_object.path
    elif isinstance(value, obj.LMIInstanceName):
        return value.wrapped_object
    elif isinstance(value, (dict, wbem.NocaseDict)):
        return wbem.NocaseDict(
            dict(
                (k, to_cim_param(t, val))
                for k, val in value.iteritems()))
    elif isinstance(value, list):
        return [to_cim_param(t, val) for val in value]
    elif isinstance(value, tuple):
        return (to_cim_param(t, val) for val in value)
    return cast.to_cim(t, value)


def to_cim_path(inst):
    '''
    Returns :py:class:`wbem.CIMInstanceName` out of inst.
    '''
    # TODO: maybe add LMIInstance(Name)
    if isinstance(inst, wbem.CIMInstance):
        return inst.path
    elif isinstance(inst, wbem.CIMInstanceName):
        return inst
    else:
        raise TypeError('inst')
