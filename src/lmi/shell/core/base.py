from abc import abstractmethod
from lmi.shell.core.cache import CacheBase

class ClientBase(CacheBase):
    def __init__(self):
        super(ClientBase, self).__init__()

    @abstractmethod
    def verify_connection(self):
        pass
