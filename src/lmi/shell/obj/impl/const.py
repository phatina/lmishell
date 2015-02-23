import abc
import re
from lmi.shell.logger import logger
from lmi.shell.util import cast


class LMIConstantValues(object):
    '''
    Abstract class for constant value objects.

    :param cim_obj: this object is either of type
        :py:class:`wbem.CIMParameter`, :py:class:`wbem.CIMProperty` or
        :py:class:`wbem.CIMMethod`. Construction of this object requires to
        have a member ``cast_type`` to properly cast CIM object. When
        constructing derived objects, make sure, that the mentioned member is
        present before calling this constructor.
    :param cast_type: parameter/property cast type
    '''
    __metaclass__ = abc.ABCMeta

    def __init__(self, cim_obj, cast_type):
        items = zip(
            cim_obj.qualifiers['Values'].value,
            cim_obj.qualifiers['ValueMap'].value)
        self.value_map = {}
        self.value_map_inv = {}
        self.cast_type = cast_type
        # Fill two dictionaries for bidirectional access to constant values.
        cnt = 1
        for key, value in items:
            try:
                # Cast constant value first. If we get ValueError, no key
                # modifications are necessary.
                val = cast.to_lmi(self.cast_type, value)

                # Keys can contain various undesirable characters, such as
                # python operators, etc. So we drop them.
                mod_key = re.sub('\W', '', key)
                if mod_key[0].isdigit():
                    mod_key = 'Key_' + mod_key
                if mod_key in self.value_map:
                    mod_key += str(cnt)
                    cnt += 1
                    logger.warn('Constant value mapped as: \'%s\' -> \'%s\'' %
                                (key, mod_key))

                self.value_map[mod_key] = val
                # For inverse mapping, we use unmodified key.
                self.value_map_inv[val] = key
            except ValueError, e:
                # Can not cast such value as interval. Can be found in
                # DMTFReserved, VendorReserved values.
                pass

    def __repr__(self):
        '''
        Returns a string of all constant names with corresponding value.

        :returns: pretty string
        '''
        return '\n'.join([
            '%s = %s' % (k, v)
            for k, v in self.value_map.iteritems()])

    def __getattr__(self, name):
        '''
        Returns either a member of the class, or a constant value.

        Simplifies the code and constant value can be retrieved by
        :samp:`object.constant_value`.

        :param string name: member to retrieve
        :returns: class member
        '''
        if name in self.value_map:
            return self.value_map[name]
        raise AttributeError(name)

    def values_dict(self):
        '''
        :returns: dictionary of constants' names and values
        '''
        return self.value_map

    def values(self):
        '''
        :returns: list of all available constant values
        '''
        return self.value_map.keys()

    def value(self, value_name):
        '''
        :param string value_name: constant name
        :returns: constant value

        **Usage:** :ref:`class_get_valuemap_property_value`.
        '''
        return getattr(self, value_name)

    def value_name(self, value):
        '''
        :param int value: numeric constant value
        :returns: constant value
        :rtype: string

        **Usage:** :ref:`class_get_valuemap_property_name`.
        '''
        return self.value_map_inv[value]


class LMIConstantValuesParamProp(LMIConstantValues):
    '''
    Derived class used for constant values of :py:class:`wbem.CIMProperty` and
    :py:class:`wbem.CIMParameter`.

    :param cim_property: :py:class:`wbem.CIMProperty` or
        :py:class:`wbem.CIMParameter` object. Both objects have necessary
        member ``type`` which is needed for proper casting.
    '''
    def __init__(self, cim_property):
        super(LMIConstantValuesParamProp, self).__init__(
            cim_property, cim_property.type)


class LMIConstantValuesMethodReturnType(LMIConstantValues):
    '''
    Derived class used for constant values of :py:class:`wbem.CIMMethod`.

    :param CIMMethod cim_method: :py:class:`wbem.CIMMethod` object
    '''
    def __init__(self, cim_method):
        super(LMIConstantValuesMethodReturnType, self).__init__(
            cim_method, cim_method.return_type)
