class SetAttrMeta(type):
    '''
    Meta class for all other classes, which use __setattr__ and want to assign
    attributes in __init__ without using __dict__[attr] = value.
    '''
    def __new__(mcls, name, bases, attrs):
        def __setattr__(self, attr, value):
            object.__setattr__(self, attr, value)

        init_attrs = dict(attrs)
        init_attrs['__setattr__'] = __setattr__

        init_cls = super(SetAttrMeta, mcls).__new__(mcls, name, bases, init_attrs)
        init_cls.real_cls = super(SetAttrMeta, mcls).__new__(mcls, name, (init_cls,), attrs)

        return init_cls

    def __call__(cls, *args, **kwargs):
        self = super(SetAttrMeta, cls).__call__(*args, **kwargs)
        self.__class__ = cls.real_cls
        return self


