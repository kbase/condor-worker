#!/bin/bash

# If there is an environment variable "POOL_PASSWORD" write it out to the pool
# condor pool password

if [ "$GROUPMOD_DOCKER" ] ; then
    groupmod -g $GROUPMOD_DOCKER docker
fi

if [ "$POOL_PASSWORD" ] ; then
    /usr/sbin/condor_store_cred -p "$POOL_PASSWORD" -f "$(condor_config_val SEC_PASSWORD_FILE)"
    condor_store_cred -p "$POOL_PASSWORD" -c add
    umask 0077; condor_token_create -identity condor@mypool > /etc/condor/tokens.d/condor@mypool
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

# Set up directory for jobs to run in, as well as a place for logs to go after a job is done.
# Not sure which one of these paths will be used for logs yet

if [ "$CONDOR_SUBMIT_WORKDIR" ] ; then
    mkdir -p "${CONDOR_SUBMIT_WORKDIR}/${EXECUTE_SUFFIX}"
    chmod 01777 "$CONDOR_SUBMIT_WORKDIR/${EXECUTE_SUFFIX}"
    chmod 01777 "$CONDOR_SUBMIT_WORKDIR/logs"
    chmod 01777 "$CONDOR_SUBMIT_WORKDIR/${EXECUTE_SUFFIX}/logs"
    chmod 01777 "$CONDOR_SUBMIT_WORKDIR/${EXECUTE_SUFFIX}/../logs"
else
    mkdir -p "/cdr/${EXECUTE_SUFFIX}"
    chmod 01777 "/cdr/${EXECUTE_SUFFIX}"
    chmod 01777 "/cdr/${EXECUTE_SUFFIX}/logs"
    chmod 01777 "/cdr/${EXECUTE_SUFFIX}/../logs"
fi

# Ensure condor user can write to logs, since this is now mounted from host
# Ensure condor user can modify the lock files and run files as of 8.9.10
chown condor $(condor_config_val log) $(condor_config_val lock) $(condor_config_val run)





docker system prune -a -f
exec "$(condor_config_val MASTER)" -f -t 2>&1
