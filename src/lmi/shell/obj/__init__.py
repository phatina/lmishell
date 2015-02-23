__all__ = [
    'CIMBase',
    'LMIBase',
    'LMINamespace',
    'LMIClass',
    'LMIInstance',
    'LMIInstanceName',
    'LMIMethod',
    'LMIConstantValuesParamProp',
    'LMIConstantValuesMethodReturnType',
]

from impl.base import CIMBase, LMIBase


# Proxy classes for actual implementations of CIM classes. This code is
# necessary, because we want to have every CIM module separated and in
# the implementation, there is a circular dependency.
class _LMIProxy(object):
    '''
    Proxy class for descendant
    '''
    def __init__(self, module_name, cls_name):
        self.module_name = module_name
        self.cls_name = cls_name

    def __getattr__(self, name):
        return getattr(self.cls, name)

    def __call__(self, *args, **kwargs):
        return self.cls(*args, **kwargs)

    @property
    def cls(self):
        m = __import__(
            'lmi.shell.obj.impl.%s' % self.module_name,
            fromlist=[self.cls_name])
        return getattr(m, self.cls_name)


class _LMINamespaceProxy(_LMIProxy):
    def __init__(self):
        super(_LMINamespaceProxy, self).__init__('ns', 'LMINamespace')


class _LMIClassProxy(_LMIProxy):
    def __init__(self):
        super(_LMIClassProxy, self).__init__('cls', 'LMIClass')


class _LMIInstanceProxy(_LMIProxy):
    def __init__(self):
        super(_LMIInstanceProxy, self).__init__('inst', 'LMIInstance')


class _LMIInstanceNameProxy(_LMIProxy):
    def __init__(self):
        super(_LMIInstanceNameProxy, self).__init__('instname', 'LMIInstanceName')


class _LMIMethodProxy(_LMIProxy):
    def __init__(self):
        super(_LMIMethodProxy, self).__init__('method', 'LMIMethod')


class _LMIConstantValuesParamPropProxy(_LMIProxy):
    def __init__(self):
        super(_LMIConstantValuesParamPropProxy, self).__init__(
            'const', 'LMIConstantValuesParamProp')


class _LMIConstantValuesMethodReturnTypeProxy(_LMIProxy):
    def __init__(self):
        super(_LMIConstantValuesMethodReturnTypeProxy, self).__init__(
            'const', 'LMIConstantValuesMethodReturnType')


LMINamespace = _LMINamespaceProxy()
LMIClass = _LMIClassProxy()
LMIInstance = _LMIInstanceProxy()
LMIInstanceName = _LMIInstanceNameProxy()
LMIMethod = _LMIMethodProxy()
LMIConstantValuesParamProp = _LMIConstantValuesParamPropProxy()
LMIConstantValuesMethodReturnType = _LMIConstantValuesMethodReturnTypeProxy()
