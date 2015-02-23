from lmi.shell import exc, util
from lmi.shell.core import base, wbem
from lmi.shell.core.cache import cached


@exc.cwrap
class CIMXMLClient(base.ClientBase, wbem.WBEMConnection):
    '''
    CIM-XML Client.
    '''
    def __init__(self, uri, username='', password='', key_file=None,
            cert_file=None, verify_server_cert=True, use_cache=True):
        creds = (username, password)
        x509 = {'cert_file': cert_file, 'key_file': key_file}
        if util.is_negative(creds) is True:
            creds=None
        if util.is_negative(x509) is True:
            x509 = None

        base.ClientBase.__init__(self)
        wbem.WBEMConnection.__init__(
            self, uri, creds, x509,
            no_verification=not verify_server_cert)

        self.use_cache = use_cache
        self.supports_pull = wbem.config.SUPPORTS_PULL_OPERATIONS

    def __repr__(self):
        return u'%s(url=%s, ...)' % (self.__class__.__name__, repr(self.url))

    def verify_connection(self):
        try:
            # This should raise CIMError.
            self.GetClass('RaiseCIMErrorClass')
        except exc.CIMError as e:
            # Yes, we are good. Connection is working.
            return

    @cached
    def EnumerateClasses(self, namespace=None, ClassName=None,
                         DeepInheritance=False, LocalOnly=True,
                         IncludeQualifiers=True, IncludeClassOrigin=False):
        return wbem.WBEMConnection.EnumerateClasses(
            self, namespace, ClassName, DeepInheritance, LocalOnly,
            IncludeQualifiers, IncludeClassOrigin)

    @cached
    def EnumerateClassNames(self, namespace=None, ClassName=None,
                            DeepInheritance=False):
        return wbem.WBEMConnection.EnumerateClassNames(
            self, namespace, ClassName, DeepInheritance)

    @cached
    def GetClass(self, ClassName, namespace=None, LocalOnly=True,
                 IncludeQualifiers=True, IncludeClassOrigin=False,
                 PropertyList=None):
        cim_class = wbem.WBEMConnection.GetClass(
            self, ClassName, namespace, LocalOnly, IncludeQualifiers,
            IncludeClassOrigin, PropertyList)
        cim_class.namespace = namespace
        return cim_class
