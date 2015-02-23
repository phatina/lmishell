from abc import abstractmethod
from lmi.shell import exc
from lmi.shell.util import query


MAX_OBJECT_CNT = 16


class OPBase(object):
    '''
    Base class for Enumerator operations.
    '''
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.ctx = None
        self.end = False
        self.cnt = 0
        self.limit = -1
        self.query = None

    def __call__(self, client):
        if client.supports_pull:
            method = self.make_method(client)
            args, kwargs = self.make_method_args()

            try:
                # Get a batch of elements.
                elements, self.ctx, self.end = method(*args, **kwargs)
                self.cnt += len(elements)

                if self.limit >= 0 and self.cnt > self.limit:
                    limit = self.limit - len(elements)
                    self.end = True
                    client.CloseEnumeration(self.ctx)
                    return elements[:limit]

                return elements
            except exc.CIMError as e:
                if e.args[0] == wbem.CIM_ERR_NOT_SUPPORTED:
                    client.supports_pull = False
                    self.ctx = None
                    self.end = True
                else:
                    raise

        if not client.supports_pull:
            method = self.make_method(client, False)
            args, kwargs = self.make_method_args(False)

            # Get all the elements.
            elements = method(*args, **kwargs)

            # This type of call doesn't return end flag. We need to set this by
            # hand.
            self.end = True

            return elements

    @classmethod
    def method_name(cls):
        return cls.__name__[2:]

    def finished(self):
        return self.end

    def make_method_args(self, use_pull=True):
        if use_pull:
            if self.ctx is None:
                kwargs = self.kwargs.copy()
                kwargs['MaxObjectCnt'] = 0
                return self.args, kwargs
            else:
                return [self.ctx], {'MaxObjectCnt': MAX_OBJECT_CNT}
        else:
            return self.args, self.kwargs

    def make_method(self, client, use_pull=True):
        method_name = self.method_name()
        if use_pull:
            if self.ctx is None:
                method_name = 'Open' + method_name
            else:
                method_name = self.PULL_METHOD
        return getattr(client, method_name)

    def set_filter(self, inst_filter):
        self.query = query.Query(inst_filter)

    def set_limit(self, limit):
        if limit < -1:
            raise ValueError('limit out of range <-1, inf)')
        self.limit = limit


class OPInstanceNamesBase(OPBase):
    '''
    Base class for InstanceNames enumerate operations.
    '''
    PULL_METHOD = 'PullInstanceNames'


class OPInstancesBase(OPBase):
    '''
    Base class for Instances enumerate operations.
    '''
    PULL_METHOD = 'PullInstances'


class OPEnumerateInstanceNames(OPInstanceNamesBase):
    def __init__(self, ClassName, namespace=None):
        super(OPEnumerateInstanceNames, self).__init__(ClassName, namespace)


class OPEnumerateInstances(OPInstancesBase):
    def __init__(self, ClassName, namespace=None, LocalOnly=True,
                 DeepInheritance=True, IncludeQualifiers=False,
                 IncludeClassOrigin=False, PropertyList=None):
        super(OPEnumerateInstances, self).__init__(
            ClassName, namespace=namespace,
            LocalOnly=LocalOnly,
            DeepInheritance=DeepInheritance,
            IncludeQualifiers=IncludeQualifiers,
            IncludeClassOrigin=IncludeClassOrigin,
            PropertyList=PropertyList)


class OPAssociators(OPInstancesBase):
    def __init__(self, ObjectName, namespace=None, AssocClass=None,
                 ResultClass=None, Role=None, ResultRole=None,
                 IncludeQualifiers=False, IncludeClassOrigin=False,
                 PropertyList=None):
        super(OPAssociators, self).__init__(
            ObjectName, namespace=namespace, AssocClass=AssocClass,
            ResultClass=ResultClass, Role=Role, ResultRole=ResultRole,
            IncludeQualifiers=IncludeQualifiers,
            IncludeClassOrigin=IncludeClassOrigin, PropertyList=PropertyList)


class OPAssociatorNames(OPInstanceNamesBase):
    def __init__(self, ObjectName, namespace=None, AssocClass=None,
                 ResultClass=None, Role=None, ResultRole=None):
        super(OPAssociatorNames, self).__init__(
            ObjectName, namespace=namespace, AssocClass=AssocClass,
            ResultClass=ResultClass, Role=Role, ResultRole=ResultRole)


class OPReferences(OPInstancesBase):
    def __init__(self, ObjectName, namespace=None, ResultClass=None, Role=None,
                 IncludeQualifiers=False, IncludeClassOrigin=False,
                 PropertyList=None):
        super(OPInstancesBase, self).__init__(
            ObjectName, namespace=namespace,
            ResultClass=ResultClass, Role=Role,
            IncludeQualifiers=IncludeQualifiers,
            IncludeClassOrigin=IncludeClassOrigin, PropertyList=PropertyList)


class OPReferenceNames(OPInstanceNamesBase):
    def __init__(self, ObjectName, namespace=None, ResultClass=None,
                 Role=None):
        super(OPReferenceNames, self).__init__(ObjectName, namespace=namespace,
            ResultClass=ResultClass, Role=Role)


# ------------------------------------------------------------------------------
# Enumerator class.
#
# Example of usage:
# -----------------
#
# op = OPEnumerateInstances('CIM_Account')
# op.set_limit(16)                 # Get first 16 objects
# enumerator = Enumerator(client)  # client is instance of ClientBase
# enumerator.set_operation(op)
#
# for elem in enumerator:
#     do_something_with(elem)
# ------------------------------------------------------------------------------


class Enumerator(object):
    '''
    Enumeration provider.
    '''
    def __init__(self, client, op=None):
        self.client = client
        self.op = op

    def __iter__(self):
        if self.op is None:
            raise ValueError('set_operation() must precede __iter__()')

        while True:
            elements = self.op(self.client)
            for element in elements:
                yield element
            if self.op.finished():
                break

    def validate_operation(self, op=None):
        op = op or self.op
        if not isinstance(op, OPBase):
            raise TypeError('op must be OPBase type')

    def set_operation(self, op):
        self.validate_operation(op)
        self.op = op
