#!/bin/bash

# See documentation at https://github.com/htcondor/htcondor/tree/main/build/docker/services#providing-additional-configuration

######################## Required Values BEGIN ########################################
if [ "$CONDOR_JWT_TOKEN" ] ; then
    echo "$CONDOR_JWT_TOKEN" > /etc/condor/tokens.d/JWT
    chmod 600 /etc/condor/tokens.d/JWT
fi

if [ "$COLLECTOR_HOST" ] ; then
    echo "COLLECTOR_HOST = $COLLECTOR_HOST" >> /etc/condor/condor_config.local
fi

# This has to be the same exact path as the mount otherwise the JobRunner doesn't understand relative mounts
# e.g. You cannot mount /cdr/staging as /execute, you must mount /cdr/staging as /cdr/staging
if [ "$EXECUTE" ] ; then
  echo "EXECUTE = $EXECUTE" >> /etc/condor/condor_config.local
fi
######################## Required Values END ##########################################

#Note the clientgroup will require quotation marks in the env variable
if [ "$CLIENTGROUP" ] ; then
    echo "CLIENTGROUP = $CLIENTGROUP" >> /etc/condor/condor_config.local
fi

# To keep docker partition from filling up
if [ "$DOCKER_SYSTEM_PRUNE" ] ; then
    docker system prune -a -fg
fi





#TODO Make nobody user able to run jobs
####################### HOST PATHS ############################################
DIRS_TO_CREATE=$(condor_config_val DIRS_TO_CREATE)
mkdir -p $DIRS_TO_CREATE
chmod 01777 $DIRS_TO_CREATE && chown root:condor $DIRS_TO_CREATE

# /condor/execute root-squashed or not condor-owned: requiring world-writability
chmod 01777 $(condor_config_val EXECUTE)
chmod 01777 $(condor_config_val DOCKER_SOCKET)
####################### HOST PATHS ############################################
/update-config