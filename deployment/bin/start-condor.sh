#!/bin/bash

# If there is an environment variable "POOL_PASSWORD" write it out to the pool
# condor pool password
if [ "$POOL_PASSWORD" ] ; then
    /usr/sbin/condor_store_cred -p "$POOL_PASSWORD" -f `condor_config_val SEC_PASSWORD_FILE`
fi

if [ "$SET_NOBODY_USER_GUID" ] ; then
    usermod -a -G "$SET_NOBODY_USER_GUID" nobody
# For backwards compatibility for directories already created by the kbase user
    usermod -a -G "kbase" nobody
fi

if [ "$SET_NOBODY_USER_UID" ] ; then
    usermod -u "$SET_NOBODY_USER_UID" nobody -o
fi

if [ "$condor_submit_workdir" ] ; then
    mkdir -p $condor_submit_workdir
else
    mkdir -p /mnt/awe/condor/condor_job_execute
fi


exec /usr/sbin/condor_master -f -t 2>&1 
