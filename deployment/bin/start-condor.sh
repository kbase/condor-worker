#!/bin/bash

# If there is an environment variable "POOL_PASSWORD" write it out to the pool
# condor pool password
if [ "$POOL_PASSWORD" ] ; then
    /usr/sbin/condor_store_cred -p "$POOL_PASSWORD" -f `condor_config_val SEC_PASSWORD_FILE`
fi

if [ "$SET_NOBODY_USER_GUID" ] ; then
    usermod -a -G "$SET_NOBODY_USER_GUID" nobody
    usermod -a -G "$SET_NOBODY_USER_GUID" condor
# For backwards compatibility for directories already created by the kbase user
    usermod -a -G "kbase" nobody
fi

if [ "$SET_NOBODY_USER_UID" ] ; then
    usermod -u "$SET_NOBODY_USER_UID" nobody -o
fi

if [ "$CONDOR_SUBMIT_WORKDIR" ] ; then
    mkdir -p $CONDOR_SUBMIT_WORKDIR${EXECUTE_SUFFIX}
    chmod 01777 $CONDOR_SUBMIT_WORKDIR${EXECUTE_SUFFIX}
else
    mkdir -p /cdr${EXECUTE_SUFFIX}
    chmod 01777 /cdr${EXECUTE_SUFFIX}
fi



exec $(condor_config_val MASTER) -f -t 2>&1
