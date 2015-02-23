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

from functools import wraps
from lmi.shell import util


class Cache(dict):
    '''
    Cache class.
    '''
    def __init__(self, *args, **kwargs):
        super(Cache, self).__init__(*args, **kwargs)
        self.active = True

    def __setitem__(self, name, value):
        if not self.active:
            return
        dict.__setitem__(self, name, value)

    def __repr__(self):
        return '%s(elements=%d)' % (self.__class__.__name__, len(self))


class GCache(Cache):
    '''
    General cache class.
    '''
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cache, cls).__new__(cls)
        return cls._instance


class CacheBase(object):
    '''
    Cached object base class.
    '''
    def __init__(self):
        self.cache = Cache()


# Decorator used for caching a function or method call. When used with methods,
# a class must derive from CacheBase.
def cached(func):
    saved = None

    @wraps(func)
    def wrapped(*args, **kwargs):
        # Choose a cache to use.
        if len(args) >= 1 and isinstance(args[0], CacheBase):
            saved = args[0].cache
        else:
            saved = GCache()

        k = args + util.flatten(kwargs)
        if k in saved:
            return saved[k]
        result = func(*args, **kwargs)
        saved[k] = result
        return result
    return wrapped
