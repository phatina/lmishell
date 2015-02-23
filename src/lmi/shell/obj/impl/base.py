class CIMBase(object):
    '''
    Base class for CIM wrapper classes.
    '''
    def __init__(self, conn):
        self.conn = conn


class LMIBase(CIMBase):
    '''
    Base class for LMI wrapper classes.
    '''
    def __init__(self, conn):
        super(LMIBase, self).__init__(conn)

    @property
    def wrapped_object(self):
        '''
        Returns a wrapped CIM object.
        '''
        raise NotImplementedError('wrapped_object')
