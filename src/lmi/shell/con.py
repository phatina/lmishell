import os
import sys
#import atexit

import M2Crypto.SSL
import M2Crypto.SSL.Checker
import M2Crypto.X509

from lmi.shell import core
from lmi.shell import exc
from lmi.shell import obj
from lmi.shell.logger import logger
from lmi.shell.util import prompt, url, is_negative


# TODO: no exception wrapping
def connect(uri, username='', password='', key_file=None, cert_file=None,
            verify_server_cert=True, use_cache=True, prompt_prefix=''):
    '''
    Creates a connection object with provided URI and credentials.
    '''
    def is_local_connection(uri, username, password, cert_file, key_file):
        #try:
        #    os.stat('/var/run/tog-pegasus/cimxml.socket')
        #except OSError as e:
        #    return False
        return url.is_localhost(uri) and \
                is_negative(username, password, cert_file, key_file)

    # Create a connection object.
    if is_local_connection(uri, username, password, cert_file, key_file):
        # Connect via UNIX socket.
        connection = LMIConnection(uri, use_cache=use_cache)
    else:
        # If username or password is missing, prompt for one.
        if is_negative(key_file, cert_file):
            res = url.parse(uri)
            if res.creds is None:
                try:
                    if not username:
                        username = prompt.prompt_input(prompt_prefix + 'username: ')
                    if not password:
                        password = prompt.prompt_input(
                            prompt_prefix + 'password: ',
                            echo=False)
                except KeyboardInterrupt as e:
                    sys.stdout.write('\n')
                    return None
            else:
                username, password = res.creds

        # Connect via HTTP.
        connection = LMIConnection(
            str(res), username, password, key_file=key_file,
            cert_file=cert_file, verify_server_cert=verify_server_cert,
            use_cache=use_cache)

    try:
        connection.connect()
    except Exception as e:
        raise e

    logger.info('Connected to %s', uri)

    return connection


class LMIConnection(object):
    '''
    Class representing a connection object. Each desired connection to separate
    CIMOM should have its own connection object created. This class provides an
    entry point to the namespace/classes/instances/methods hierarchy present in
    the LMIShell.
    '''
    def __init__(self, uri, username='', password='', key_file=None,
            cert_file=None, verify_server_cert=True, use_cache=True):
        # Split uri into elements. Some elements of URL may be missing.
        # They are defaulted by url module.
        res = url.parse_cim(uri)

        if url.is_localhost(uri) is False:
            self.url = str(res)
        else:
            self.url = uri

        # Create a client object
        if url.is_wsman_path(res.path) is False:
            # We talk to CIMOM via CIM-XML
            self.client = core.CIMXMLClient(
                self.url, username, password,
                key_file=key_file, cert_file=cert_file,
                verify_server_cert=verify_server_cert,
                use_cache=use_cache)
        else:
            # We talk to CIMOM via WSMAN
            self.client = core.WSMANClient(
                self.url, username, password,
                key_file=key_file, cert_file=cert_file,
                verify_server_cert=verify_server_cert)

        self.indications = {}

        # TODO: add hook in ind.subscribe() to auto-unsubscribe
        # Register LMIConnection.unsubscribe_all_indications() to be called at
        # LMIShell's exit.
        #atexit.register(lambda: self.unsubscribe_all_indications())

    def __del__(self):
        '''
        Disconnects and frees :py:class:`.LMICIMXMLClient` object.
        '''
        try:
            self.client.disconnect()
            del self.client
        except AttributeError:
            pass

    def __repr__(self):
        '''
        :returns: pretty string for the object.
        '''
        return '%s(URL=%s, user=%s, ...)' % (
            self.__class__.__name__, repr(self.url), repr(self.client.creds[0]))

    @property
    def hostname(self):
        '''
        :returns: hostname of CIMOM
        '''
        return self.client.hostname

    @property
    def namespaces(self):
        '''
        :returns: list of all available namespaces

        **Usage:** :ref:`namespaces_available_namespaces`.
        '''
        return [u'root']

    @property
    def root(self):
        '''
        :returns: :py:class:`.LMINamespace` object for *root* namespace
        '''
        return obj.LMINamespace(self, u'root')

    @property
    def timeout(self):
        '''
        :returns: CIMOM connection timeout for a transaction (milliseconds)
        :rtype: int
        '''
        return self.client._cliconn.timeout

    @timeout.setter
    def timeout(self, timeout):
        '''
        Sets CIMOM connection timeout for a transaction (milliseconds).

        :param inst timeout: timeout in milliseconds
        '''
        self.client._cliconn.timeout = timeout

    def get_namespace(self, namespace):
        '''
        :param string namespace: namespace path (eg. `root/cimv2`)
        :returns: :py:class:`.LMINamespace` object
        :raises: :py:exc:`.LMINamespaceNotFound`
        '''
        def get_namespace_priv(namespace, namespace_path):
            if not namespace_path:
                return namespace
            ns = namespace_path.pop(0)
            return get_namespace_priv(getattr(namespace, ns), namespace_path)

        namespace_path = namespace.split('/')
        ns = namespace_path.pop(0)
        if ns not in self.namespaces:
            raise exc.LMINamespaceNotFound(ns)
        return get_namespace_priv(getattr(self, ns), namespace_path)

    def clear_cache(self):
        '''
        Clears the cache.
        '''
        if hasattr(self.client, 'cache'):
            self.client.cache.clear()

    def use_cache(self, active=True):
        '''
        Sets a bool flag, which defines, if the LMIShell should use a cache.

        :param bool active: whether the LMIShell's cache should be used
        '''
        if hasattr(self.client, 'cache'):
            self.client.cache.active = active

    def connect(self):
        '''
        Connects to CIMOM and verifies credentials.
        '''
        self.client.connect()
        self.client.verify_connection()

    def disconnect(self):
        '''
        Disconnects from CIMOM.
        '''
        self.client.disconnect()

    def is_wsman(self):
        '''
        Returns True, if the connection is made with WSMAN CIMOM; False
        otherwise.
        '''
        return isinstance(self.client, core.WSMANClient)
