from instbase import LMIInstanceBase  # TODO: import from obj?
from lmi.shell import obj
from lmi.shell.util import transform


class LMIInstanceName(LMIInstanceBase):
    '''
    LMI class representing CIM Instance Name.
    '''
    def __init__(self, conn, cim_inst_name):
        super(LMIInstanceName, self).__init__(conn, cim_inst_name)

    def __cmp__(self, other):
        if not isinstance(other, LMIInstanceName):
            return -1
        return cmp(self.cim_inst_name, other.cim_inst_name)

    def __contains__(self, key):
        return key in self.cim_inst_name

    def __getattr__(self, attr):
        if attr in self.cim_inst_name:
            member = self.cim_inst_name[attr]
            if isinstance(member, wbem.CIMInstanceName):
                member = transform.to_lmi(self.conn, member)
            return member
        elif not self.conn.is_wsman() and attr in self.methods:
            return obj.LMIMethod(self.conn, attr, self.cim_inst_name)
        elif self.conn.is_wsman() and not attr.startswith("_"):
            return obj.LMIMethod(self.conn, attr, self.cim_inst_name)
        raise AttributeError(attr)

    def __setattr__(self, attr, value):
        if attr in self.cim_inst_name.keys():  # TODO: remove '.keys()'?
            if isinstance(value, str):
                # Convert string value into unicode
                value = unicode(value, "utf-8")
            elif isinstance(value, (obj.LMIInstanceName, obj.LMIInstance)):
                # Unpack wrapped LMI object
                value = value.wrapped_object
            self.cim_inst_name[attr] = value
        else:
            self.__dict__[attr] = value

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return unicode(self.cim_obj)

    def __repr__(self):
        return '%s(classname="%s"...)' % (
            self.__class__.__name__,
            self.classname)

    def copy(self):
        return obj.LMIInstanceName(self.conn, self.cim_inst_name.copy())

    def to_instance(self):
        return obj.LMIInstance(
            self.conn, self.conn.client.GetInstance(
                self.cim_inst_name))

    def key_property_value(self, prop_name):
        return getattr(self, prop_name)

    @property
    def key_properties(self):
        return self.cim_inst_name.keys()

    @property
    def key_properties_dict(self):
        return self.cim_inst_name.keybindings.copy()

    @property
    def cim_inst_name(self):
        return self.cim_obj
