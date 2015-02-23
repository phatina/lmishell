from lmi.shell import exc, obj, util
from lmi.shell.core import enum, wbem
from lmi.shell.logger import logger
from lmi.shell.util import cast


class CIMClassProvider(obj.CIMBase):
    # States of CIMClass provider.
    # Available states:
    # - fetched - CIMClass has been already fetched. Consider it as minimal state.
    # - none - CIMClass will be fetched from CIMOM with minimum members.
    # - full - CIMClass will be fetched from CIMOM with all members.
    STATE_NONE, STATE_FETCHED, STATE_FULL = range(3)

    def __init__(self, conn, cim_class, namespace=None):
        super(CIMClassProvider, self).__init__(conn)
        if isinstance(cim_class, wbem.CIMClass):
            self.cim_class = cim_class
            self.classname = cim_class.classname
            self.namespace = cim_class.namespace
            self.state = self.STATE_FETCHED
        elif isinstance(cim_class, basestring):
            self.cim_class = None
            self.classname = cim_class
            self.namespace = namespace
            self.state = self.STATE_NONE
        else:
            raise TypeError('cim_class must be wbem.CIMClass or basestring type')

        if self.namespace is None:
            self.namespace = wbem.config.DEFAULT_NAMESPACE

    def get(self):
        if self.state == self.STATE_NONE:
            # XXX: Do we want to limit also other members?
            self.cim_class = self.conn.client.GetClass(
                self.classname, self.namespace,
                LocalOnly=False,
                IncludeQualifiers=False)
            self.state = self.STATE_FETCHED
        return self.cim_class

    def get_full(self):
        if self.state != self.STATE_FULL:
            self.cim_class = self.conn.client.GetClass(
                self.classname, self.namespace,
                LocalOnly=False,
                IncludeQualifiers=True)
            self.state = self.STATE_FULL
        return self.cim_class


class LMIClass(obj.LMIBase):
    '''
    LMI class representing CIM Class.
    '''
    def __init__(self, conn, cim_class, namespace=None):
        super(LMIClass, self).__init__(conn)
        self.cim_class_prov = CIMClassProvider(conn, cim_class, namespace)
        self.valuemap_properties_list = None

    def __repr__(self):
        return '%s(classname=\'%s\', ...)' % (
            self.__class__.__name__, self.classname)

    def __getattr__(self, name):
        if name.endswith('Values'):
            property_name = name[:-6]
            return obj.LMIConstantValuesParamProp(
                self.cim_class_full.properties[property_name])
        raise AttributeError(name)

    def __iter__(self):
        for inst_name in self.instance_names():
            yield inst_name

    @staticmethod
    def wrap(conn, cim_class):
        return LMIClass(conn, cim_class)

    @staticmethod
    def make(conn, classname, namespace):
        return LMIClass(conn, classname, namespace)

    def create_instance(self, properties=None, qualifiers=None,
                        property_list=None):
        #if self.conn.is_wsman():
        #    # WSMAN client doesn't support CreateInstance()
        #    logger().info("WSMAN client doesn't support CreateInstance()")
        #    return None

        # No need to copy dictionaries to avoid the variable mix-up, the
        # copying is done in client.CreateInstance(), we just pass
        # what we get.
        properties = properties or wbem.NocaseDict()
        qualifiers = qualifiers or wbem.NocaseDict()
        self_properties = self.cim_class.properties
        for key, value in properties.iteritems():
            if key not in self_properties:
                raise exc.LMIUnknownPropertyError(
                    'No such instance property \'%s\'' % key)
            if isinstance(value, obj.LMIInstanceName):
                value = value.wrapped_object
            t = self_properties[key].type
            properties[key] = cast.to_cim(t, value)
        return obj.LMIInstanceName(
            self.conn,
            self.conn.client.CreateInstance(
                wbem.CIMInstance(
                    self.classname,
                    properties,
                    qualifiers,
                    None,
                    property_list)))

    def doc(self):
        raise NotImplementedError('doc')

    def instance_names(self, inst_filter=None, limit=-1):
        op = enum.OPEnumerateInstanceNames(
            self.classname,
            self.namespace)
        op.set_filter(inst_filter)
        op.set_limit(limit)
        enumerator = enum.Enumerator(self.conn.client)
        enumerator.set_operation(op)
        for inst_name in enumerator:
            yield obj.LMIInstanceName(self.conn, inst_name)

    def first_instance_name(self, inst_filter=None):
        return util.generator_first(self.instance_names(inst_filter, limit=1))

    def new_instance_name(self, keybindings):
        kbs = wbem.NocaseDict()
        for key, value in keybindings.iteritems():
            if isinstance(value, obj.LMIInstanceName):
                value = value.wrapped_object
            elif isinstance(value, str):
                # Convert strings to unicode
                value = unicode(value, "utf-8")
            kbs[key] = value
        cim_inst_name = wbem.CIMInstanceName(
            self.classname, kbs, namespace=self.namespace)
        return obj.LMIInstanceName(self.conn, cim_inst_name)


    def instances(self, inst_filter=None, limit=-1, LocalOnly=True,
                  DeepInheritance=True, IncludeQualifiers=False,
                  IncludeClassOrigin=False, PropertyList=None):
        op = enum.OPEnumerateInstances(
            self.classname,
            namespace=self.namespace,
            LocalOnly=LocalOnly,
            DeepInheritance=DeepInheritance,
            IncludeQualifiers=IncludeQualifiers,
            IncludeClassOrigin=IncludeClassOrigin,
            PropertyList=PropertyList)
        op.set_filter(inst_filter)
        op.set_limit(limit)
        enumerator = enum.Enumerator(self.conn.client)
        enumerator.set_operation(op)
        for inst in enumerator:
            yield obj.LMIInstance(self.conn, inst)

    def first_instance(self, inst_filter=None, LocalOnly=True,
                  DeepInheritance=True, IncludeQualifiers=False,
                  IncludeClassOrigin=False, PropertyList=None):
        return util.generator_first(
            self.instances(
                inst_filter, limit=1,
                LocalOnly=LocalOnly,
                DeepInheritance=DeepInheritance,
                IncludeQualifiers=IncludeQualifiers,
                IncludeClassOrigin=IncludeClassOrigin,
                PropertyList=PropertyList))

    @property
    def valuemap_properties(self):
        if self.valuemap_properties_list is None:
            self.valuemap_properties_list = [
                k for k, v in self.cim_class_full.properties.iteritems()
                if 'ValueMap' in v.qualifiers and 'Values' in v.qualifiers]
        return self.valuemap_properties_list

    @property
    def properties(self):
        return self.cim_class.properties.keys()

    @property
    def methods(self):
        return self.cim_class.methods.keys()

    @property
    def classname(self):
        return self.cim_class_prov.classname

    @property
    def namespace(self):
        # XXX: Maybe return LMINamespace?
        return self.cim_class_prov.namespace

    @property
    def cim_class(self):
        return self.cim_class_prov.get()

    @property
    def cim_class_full(self):
        return self.cim_class_prov.get_full()

    @property
    def wrapped_object(self):
        return self.cim_class
