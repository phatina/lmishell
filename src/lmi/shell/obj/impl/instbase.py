from lmi.shell import obj, util
from lmi.shell.core import enum, wbem
from lmi.shell.util import meta, transform


class LMIInstanceBase(obj.LMIBase):
    '''
    Base class for :py:class:`.LMIInstance` and :py:class:`.LMIInstanceName`.
    '''
    __metaclass__ = meta.SetAttrMeta

    def __init__(self, conn, cim_obj):
        super(LMIInstanceBase, self).__init__(conn)
        if not isinstance(cim_obj, (wbem.CIMInstance, wbem.CIMInstanceName)):
            raise TypeError('cim_obj must be CIMInstance(Name) type')
        self.cim_obj = cim_obj

    def associator_names(self, limit=-1, AssocClass=None, ResultClass=None,
                         Role=None, ResultRole=None):
        op = enum.OPAssociatorNames(
            transform.to_cim_path(self.cim_obj),
            namespace=self.namespace, AssocClass=AssocClass,
            ResultClass=ResultClass, Role=Role, ResultRole=ResultRole)
        op.set_limit(limit)
        enumerator = enum.Enumerator(self.conn.client)
        enumerator.set_operation(op)
        for assoc_name in enumerator:
            yield obj.LMIInstanceName(self.conn, assoc_name)

    def first_associator_name(self, AssocClass=None, ResultClass=None,
                              Role=None, ResultRole=None):
        return util.generator_first(
            self.instances(
                limit=1,
                AssocClass=AssocClass, ResultClass=ResultClass, Role=Role,
                ResultRole=ResultRole))

    def associators(self, limit=-1, AssocClass=None, ResultClass=None,
                    Role=None, ResultRole=None, IncludeQualifiers=False,
                    IncludeClassOrigin=False, PropertyList=None):
        op = enum.OPAssociators(
            transform.to_cim_path(self.cim_obj),
            namespace=self.namespace, AssocClass=AssocClass,
            ResultClass=ResultClass, Role=Role, ResultRole=ResultRole,
            IncludeQualifiers=IncludeQualifiers,
            IncludeClassOrigin=IncludeClassOrigin, PropertyList=PropertyList)
        op.set_limit(limit)
        enumerator = enum.Enumerator(self.conn.client)
        enumerator.set_operation(op)
        for assoc in enumerator:
            yield obj.LMIInstance(self.conn, assoc)

    def first_associators(self, AssocClass=None, ResultClass=None, Role=None,
                          ResultRole=None, IncludeQualifiers=False,
                          IncludeClassOrigin=False, PropertyList=None):
        return util.generator_first(
            self.instance_names(
                limit=1,
                AssocClass=AssocClass, ResultClass=ResultClass, Role=Role,
                ResultRole=ResultRole, IncludeQualifiers=IncludeQualifiers,
                IncludeClassOrigin=IncludeClassOrigin,
                PropertyList=PropertyList))

    def reference_names(self, limit=-1, ResultClass=None, Role=None):
        op = enum.OPReferenceNames(
            transform.to_cim_path(self.cim_obj),
            namespace=self.namespace, ResultClass=ResultClass, Role=Role)
        op.set_limit(limit)
        enumerator = enum.Enumerator(self.conn.client)
        enumerator.set_operation(op)
        for ref_name in enumerator:
            yield obj.LMIInstanceName(self.conn, ref_name)

    def first_reference_name(self, ResultClass=None, Role=None):
        return util.generator_first(
            self.reference_names(
                limit=1, ResultClass=ResultClass, Role=Role))

    def references(self, limit=-1, ResultClass=None, Role=None,
                   IncludeQualifiers=False, IncludeClassOrigin=False,
                   PropertyList=None):
        op = enum.OPReferences(
            transform.to_cim_path(self.cim_obj),
            namespace=self.namespace, ResultClass=ResultClass, Role=Role,
            IncludeQualifiers=IncludeQualifiers,
            IncludeClassOrigin=IncludeClassOrigin, PropertyList=PropertyList)
        op.set_limit(limit)
        enumerator = enum.Enumerator(self.conn.client)
        enumerator.set_operation(op)
        for ref in enumerator:
            yield obj.LMIInstance(self.conn, ref)

    def first_reference(self, ResultClass=None, Role=None,
                   IncludeQualifiers=False, IncludeClassOrigin=False,
                   PropertyList=None):
        return util.generator_first(
            self.references(
                limit=1,
                ResultClass=ResultClass, Role=Role,
                IncludeQualifiers=IncludeQualifiers,
                IncludeClassOrigin=IncludeClassOrigin,
                PropertyList=PropertyList))

    def delete(self):
        self.conn.client.DeleteInstancee(transform.to_cim_path(self.cim_obj))

    @property
    def methods(self):
        return obj.LMIClass(self.conn, self.classname).methods

    @property
    def classname(self):
        return self.cim_obj.classname

    @property
    def namespace(self):
        return transform.to_cim_path(self.cim_obj).namespace

    @property
    def hostname(self):
        return transform.to_cim_path(self.cim_obj).host

    @property
    def wrapped_object(self):
        return self.cim_obj
