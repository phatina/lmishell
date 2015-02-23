
def subscribe():

        '''
        Subscribes to an indication. Indication is formed by 3 objects, where 2
        of them (filter and handler) can be provided, if the LMIShell should
        not create those 2 by itself.

        **NOTE:** Currently the call registers :py:mod:`atexit` hook, which
        auto-deletes all subscribed indications by the LMIShell.

        :param dictionary kwargs: parameters for the indication subscription

            * **Filter** (*LMIInstance*) -- if provided, the
              :py:class:`.LMIInstance` object will be used instead of creating
              a new one;
              **optional**
            * **Handler** (*LMIInstance*) -- if provided, the
              :py:class:`.LMIInstance` object will be used instead of creating
              a new one; **optional**
            * **Query** (*string*) -- string containing a query for the
              indications filtering
            * **QueryLanguage** (*string*) -- query language; eg. *WQL*, or
              *DMTF:CQL*.  This parameter is optional, default value is
              *DMTF:CQL*.
            * **Name** (*string*) -- indication name
            * **CreationNamespace** (*string*) -- creation namespace. This
              parameter is optional, default value is *root/interop*.
            * **SubscriptionCreationClassName** (*string*) -- subscription
              object class name. This parameter is optional, default value is
              *CIM_IndicationSubscription*.
            * **Permanent** (*bool*) -- whether to preserve the created
              subscription on LMIShell's quit. Default value is False.
            * **FilterCreationClassName** (*string*) -- creation class name of
              the filter object. This parameter is options, default value is
              *CIM_IndicationFilter*.
            * **FilterSystemCreationClassName** (*string*) -- system creation
              class name of the filter object. This parameter is optional,
              default value is *CIM_ComputerSystem*.
            * **FilterSourceNamespace** (*string*) -- local namespace where the
              indications originate. This parameter is optional, default value
              is *root/cimv2*.
            * **HandlerCreationClassName** (*string*) -- creation class name of
              the handler object. This parameter is optional, default value is
              *CIM_IndicationHandlerCIMXML*.
            * **HandlerSystemCreationClassName** (*string*) -- system creation
              name of the handler object. This parameter is optional, default
              value is *CIM_ComputerSystem*.
            * **Destination** (*string*) -- destination URI, where the
              indications should be delivered
        '''

    if self.is_wsman():
        raise TypeError('Indication subscription not supported')

    try:
        indication_namespace = kwargs.get(
            'CreationNamespace', 'root/interop')
        cim_filter_provided = 'Filter' in kwargs
        if cim_filter_provided:
            filt = kwargs['Filter']
            cim_filter = None
            if isinstance(filt, LMIObjectFactory().LMIInstance):
                cim_filter = filt._cim_instance
            elif isinstance(filt, wbem.CIMInstance):
                cim_filter = filt
            else:
                errorstr = 'Filter argument accepts instances of ' \
                    'CIMInstance or LMIInstance'
                lmi_raise_or_dump_exception(LMIIndicationError(errorstr))
                return LMIReturnValue(rval=False, errorstr=errorstr)
        else:
            cim_filter_props = {
                'CreationClassName': kwargs.get(
                    'FilterCreationClassName',
                    'CIM_IndicationFilter'),
                'SystemCreationClassName': kwargs.get(
                    'FilterSystemCreationClassName',
                    'CIM_ComputerSystem'),
                'SourceNamespace': kwargs.get(
                    'FilterSourceNamespace',
                    'root/cimv2'),
                'SystemName': self.client.uri,
                'Query': kwargs['Query'],
                'QueryLanguage': kwargs.get(
                    'QueryLanguage',
                    LMICIMXMLClient.QUERY_LANG_CQL),
                'Name': kwargs['Name'] + '-filter'
            }
            cim_filter, _, errorstr = self.client.create_instance(
                cim_filter_props['CreationClassName'],
                indication_namespace,
                self.hostname,
                cim_filter_props
            )
            if not cim_filter:
                lmi_raise_or_dump_exception(LMIIndicationError(errorstr))
                return LMIReturnValue(rval=False, errorstr=errorstr)
        cim_handler_provided = 'Handler' in kwargs
        if cim_handler_provided:
            cim_handler = kwargs['Handler']._cim_instance
        else:
            cim_handler_props = {
                'CreationClassName': kwargs.get(
                    'HandlerCreationClassName',
                    'CIM_IndicationHandlerCIMXML'),
                'SystemCreationClassName': kwargs.get(
                    'HandlerSystemCreationClassName',
                    'CIM_ComputerSystem'),
                'SystemName': self.client.uri,
                'Destination': '%s/CIMListener/%s' % (
                    kwargs['Destination'],
                    kwargs['Name']),
                'Name': kwargs['Name'] + '-handler'
            }
            cim_handler, _, errorstr = self.client.create_instance(
                cim_handler_props['CreationClassName'],
                indication_namespace,
                self.hostname,
                cim_handler_props)
            if not cim_handler:
                if 'Filter' not in kwargs:
                    self.client.delete_instance(cim_filter.path)
                lmi_raise_or_dump_exception(LMIIndicationError(errorstr))
                return LMIReturnValue(rval=False, errorstr=errorstr)
        cim_subscription_props = {
            'Filter': cim_filter.path,
            'Handler': cim_handler.path
        }
        cim_subscription, _, errorstr = self.client.create_instance(
            kwargs.get(
                'SubscriptionCreationClassName',
                'CIM_IndicationSubscription'),
            indication_namespace,
            self.hostname,
            cim_subscription_props)
        if not cim_subscription:
            if 'Filter' not in kwargs:
                self.client.delete_instance(cim_filter.path)
            if 'Handler' not in kwargs:
                self.client.delete_instance(cim_handler.path)
            lmi_raise_or_dump_exception(LMIIndicationError(errorstr))
            return LMIReturnValue(rval=False, errorstr=errorstr)
        # XXX: Should we auto-delete all the indications?
        permanent = kwargs.get('Permanent', False)
        self._indications[kwargs['Name']] = LMISubscription(
            self.client,
            (cim_filter, not cim_filter_provided),
            (cim_handler, not cim_handler_provided),
            cim_subscription,
            permanent)
    except KeyError, e:
        errorstr = 'Not all necessary parameters provided, missing: %s' % e
        lmi_raise_or_dump_exception(LMIIndicationError(errorstr))
        return LMIReturnValue(rval=False, errorstr=errorstr)
    return LMIReturnValue(rval=True)

def unsubscribe_indication(self, name):
    '''
    Unsubscribes an indication.

    :param string name: indication name
    :returns: :py:class:`.LMIReturnValue` object with ``rval`` set to True,
        if unsubscribed; False otherwise
    '''
    if name not in self._indications:
        errorstr = 'No such indication'
        lmi_raise_or_dump_exception(LMIIndicationError(errorstr))
        return LMIReturnValue(rval=False, errorstr=errorstr)
    indication = self._indications.pop(name)
    indication.delete()
    return LMIReturnValue(rval=True)

def unsubscribe_all_indications(self):
    '''
    Unsubscribes all the indications. This call ignores *Permanent* flag,
    which may be provided in
    :py:meth:`.LMIConnection.subscribe_indication`, and deletes all the
    subscribed indications.
    '''
    for subscription in self._indications.values():
        if not subscription.permanent:
            subscription.delete()
    self._indications = {}

def print_subscribed_indications(self):
    '''
    Prints out all the subscribed indications.
    '''
    for i in self._indications.keys():
        sys.stdout.write('%s\n' % i)

def subscribed_indications(self):
    '''
    :returns: list of all the subscribed indications
    '''
    return self._indications.keys()
