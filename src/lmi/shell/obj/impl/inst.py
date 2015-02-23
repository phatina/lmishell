from instbase import LMIInstanceBase  # TODO: import from obj?
from lmi.shell import obj
from lmi.shell.util import cast, transform


class LMIInstance(LMIInstanceBase):
    '''
    LMI class representing CIM Instance.
    '''
    def __init__(self, conn, cim_inst):
        super(LMIInstance, self).__init__(conn, cim_inst)

    def __cmp__(self, other):
        if not isinstance(other, LMIInstance):
            return -1
        return cmp(self.cim_inst, other.cim_inst)

    def __contains__(self, key):
        return key in self.cim_inst

    def __getattr__(self, attr):
        if attr in self.cim_inst:
            member = self.cim_inst.properties[attr]
            if isinstance(member.value, wbem.CIMInstanceName):
                return transform.to_lmi(self._conn, member.value)
            return cast.to_lmi(member.type, member.value)
        elif not self.conn.is_wsman() and attr in self.methods:
            return obj.LMIMethod(self.conn, attr, self.path.wrapped_object)
        elif self.conn.is_wsman() and not attr.startswith("_"):
            return obj.LMIMethod(self.conn, attr, self.path.wrapped_object)
        raise AttributeError(attr)

    def __setattr__(self, attr, value):
        if isinstance(value, obj.LMIInstanceName):
            value = value.wrapped_object
        if attr in self.cim_inst:
            t = self.cim_inst.properties[attr].type
            self.cim_inst.properties[attr].value = cast.to_cim(t, value)
        else:
            self.__dict__[attr] = value

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return unicode(self.cim_inst.path)

    def __repr__(self):
        return '%s(classname=\'%s\', ...)' % (
            self.__class__.__name__, self.classname)

    def copy(self):
        return obj.LMIInstance(self.conn, self.cim_inst.copy())

    def doc(self):
        raise NotImplementedError('doc')

    def tomof(self):
        return self.cim_inst.tomof()

    def property_value(self, prop_name):
        return getattr(self, prop_name)

    def push(self):
        self.conn.client.ModifyInstance(self.cim_inst)

    def refresh(self):
        self.cim_inst = self.conn.client.GetInstance(self.cim_inst.path)

    @property
    def properties(self):
        return self.cim_inst.properties.keys()

    @property
    def properties_dict(self):
        props = self.cim_inst.properties
        return wbem.NocaseDict(
            dict((k, x.value) for k, x in props.iteritems()))

    @property
    def cim_inst(self):
        return self.cim_obj

    @property
    def path(self):
        return obj.LMIInstanceName(self.conn, self.cim_inst.path)
