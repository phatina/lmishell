from lmi.shell import obj


QUERY_TYPE_CQL = 'DMTF:CQL'
QUERY_TYPE_WQL = 'WQL'


class LMINamespace(obj.LMIBase):
    '''
    LMI class representing CIM namespace.
    '''
    _SUPPORTED_NAMESPACES = [
        u'root' + ns for ns in
            u'',
            u'/cimv2',
            u'/dcim',
            u'/interop',
            u'/PG_InterOp',
            u'/PG_Internal',
    ]

    def __init__(self, conn, name):
        super(LMINamespace, self).__init__(conn)
        if name not in self._SUPPORTED_NAMESPACES:
            raise ValueError('Not valid namespace name: \'%s\'' % name)

        self.name = name

        def make_ns(full_ns_path):
            return full_ns_path.rsplit('/')[-1]

        self.namespaces = [
            make_ns(ns) for ns in self._SUPPORTED_NAMESPACES
            if ns.startswith(name + '/')
        ]

    def __getattr__(self, name):
        ns_name = self.name + '/' + name
        if ns_name in self._SUPPORTED_NAMESPACES:
            return obj.LMINamespace(self.conn, ns_name)

        return obj.LMIClass.make(self.conn, name, self.name)

    def __repr__(self):
        return '%s(namespace=\'%s\', ...)' % (
            self.__class__.__name__, self.name)

    def __iter__(self):
        for cls in self.classes():
            yield cls

    def classes(self, DeepInheritance=None):
        return self.conn.client.EnumerateClassNames(
            self.name, DeepInheritance=DeepInheritance)

    def get_class(self, classname, LocalOnly=True, IncludeQualifiers=True,
            IncludeClassOrigin=False, PropertyList=None):
        cim_class = self.conn.client.GetClass(
            classname, self.name, LocalOnly=LocalOnly,
            IncludeQualifiers=IncludeQualifiers,
            IncludeClassOrigin=IncludeClassOrigin,
            PropertyList=PropertyList)
        return LMIClass.wrap(self.conn, cim_class)

    def query(self, query, query_lang=None):
        # Prepare a query.
        if isinstance(query, LMIClass):
            query = 'select * from %s' % query.classname
        elif not isinstance(query, basestring):
            raise TypeError('query must be string or LMIClass type')

        # Prepare a query language.
        if query_lang in (QUERY_TYPE_CQL, None):
            query_func = self.cql
        elif query_lang in (QUERY_TYPE_WQL,):
            query_func = self.wql
        else:
            raise TypeError(
                'query_lang must be either None, %s or %s' % (
                    QUERY_TYPE_CQL, QUERY_TYPE_WQL))

        # Perform a query.
        return query_func(query)

    def cql(self, query):
        cim_inst_list = self.conn.client.ExecQuery(
            QUERY_TYPE_CQL, query, self.name)
        return [LMIInstance(self.conn, cim_inst) for cim_inst in cim_inst_list]

    def wql(self, query):
        cim_inst_list = self.conn.client.ExecQuery(
            QUERY_TYPE_WQL, query, self.name)
        return [LMIInstance(self.conn, cim_inst) for cim_inst in cim_inst_list]

    # TODO: Do we need this?
    @staticmethod
    def wrap(conn, name):
        return LMINamespace(conn, name)

    def wrapped_object(self):
        # There is no such class as CIMNamespace
        return None
