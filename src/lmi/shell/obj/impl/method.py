from lmi.shell import exc, obj
from lmi.shell.util import transform


class LMIMethod(obj.LMIBase):
    '''
    LMI class representing CIM Method.
    '''
    INDICATION_JOB_CLASSNAMES = (
        'LMI_SELinuxJob',
        'LMI_StorageJob',
        'LMI_SoftwareInstallationJob',
        'LMI_SoftwareVerificationJob',
        'LMI_NetworkJob')

    # Default namespace where the indication subscriptions, used for
    # synchronous method calls, will be registered.
    INDICATION_NAMESPACE = "root/interop"

    # When performing a synchronous method call and using the polling method to
    # get a job object status, the sleep time between 2 polls doubles if it is
    # less than _POLLING_ADAPT_MAX_WAITING_TIME.
    POLLING_ADAPT_MAX_WAITING_TIME = 32

    def __init__(self, conn, method_name, cim_inst_name):
        super(LMIMethod, self).__init__(conn)

        self.method_name = method_name
        self.cim_inst_name = cim_inst_name
        self.is_sync = False
        self.valuemap_parameters_list = None

    def __call__(self, method_args=None, polling=False, refresh_instance=False,
                 **kwargs):
        # Prepare method parameters.
        method_args = self.make_method_args(method_args)

        # Call the CIM method.
        rval, rparams = client.InvokeMethod(
            self.cim_instance,
            self_method_name,
            **method_args)

        # Transform method results.
        rval = transform.to_lmi(self.conn, rval)

    def make_method_args(self, method_args=None, **kwargs):
        if method_args is None:
            method_args = dict()
        method_args.update(kwargs)
        if not self.conn.is_wsman():
            for param, value in method_args.iteritems():
                if param in self.cim_method.parameters:
                    # Cast input parameters into acceptable CIM types
                    t = self.cim_method.parameters[param].type
                    method_args[param] = transform.to_cim_param(t, value)
                else:
                    # NOTE: maybe we could check for wbem type and not to exit
                    # prematurely
                    raise exc.LMIUnknownParameterError(
                        'Unknown parameter \'%s\' for method \'%s\'' % (
                            param, self.method_name)
        else:
            for param, value in method_args.iteritems():
                method_args[param] = str(value)
        return method_args

    @property
    def cim_method(self):
        lmi_cls = obj.LMIClass(self.conn, self.cim_inst_name.classname)
        return lmi_cls.cim_cl.methods[self.method_mane]
