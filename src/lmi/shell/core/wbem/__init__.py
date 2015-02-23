# Copyright (C) 2015 Peter Hatina <phatina@redhat.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

'''
LMIShell's WBEM module. It imports WBEM backend modules and sets
necessary attributes to either LMIWBEM or PyWBEM.
'''

import sys

from lmi.shell.logger import logger

try:
    # -------------------------------------------------------------------------
    # LMIWBEM
    # -------------------------------------------------------------------------
    HAVE_LMIWBEM = True

    from lmiwbem import *

    logger.debug('Using LMIWBEM backend')

    # Compatibility exceptions due to PyWBEM.
    class Error(Exception):
        pass

    class AuthError(Error):
        pass

except ImportError, e:
    # -------------------------------------------------------------------------
    # PyWBEM
    # -------------------------------------------------------------------------
    HAVE_LMIWBEM = False

    # LMIWBEM could not be imported, fall back to PyWBEM.
    try:
        from pywbem import *
        from pywbem.cim_http import *
    except ImportError, e:
        # We can't import any backend, exit with error!
        logger.error('Can\'t import either lmiwbem or pywbem module.')
        sys.exit(1)

    logger.debug('Using PyWBEM backend')

    from lmi.shell.core.wbem.listener import CIMIndicationListener

    # Compatiblity exception due to LMIWBEM.
    class ConnectionError(Exception):
        pass

    # Compatibility class due to LMIWBEM.
    PyWBEMNocaseDict = NocaseDict
    class NocaseDict(PyWBEMNocaseDict):
        '''
        :py:class:`pywbem.NocaseDict` with compatibility API
        '''
        def get(self, key, default=None):
            if key in self:
                return self[key]
            else:
                return default

        def pop(self, key, default=None):
            if key in self:
                rval = self[key]
                del self[key]
                return rval
            else:
                return default

    EXC_VERB_NONE, \
        EXC_VERB_CALL, \
        EXC_VERB_MORE = range(3)

    class Config(object):
        '''
        :py:class:`lmiwbem.Config` compatibility class
        '''
        def __init__(self):
            self.DEFAULT_NAMESPACE = DEFAULT_NAMESPACE
            self.DEFAULT_TRUST_STORE = u'/etc/pki/ca-trust/source/anchors/'
            self.EXCEPTION_VERBOSITY = EXC_VERB_NONE

        @property
        def SUPPORTS_PULL_OPERATIONS(self):
            return False

    # Compatibility object
    config = Config()

    del PyWBEMNocaseDict
