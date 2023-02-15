#!/bin/bash

# See documentation at https://github.com/htcondor/htcondor/tree/main/build/docker/services#providing-additional-configuration

if [ "$CONDOR_JWT_TOKEN" ] ; then
    echo "$CONDOR_JWT_TOKEN" > /etc/condor/tokens.d/JWT
    chmod 600 /etc/condor/tokens.d/JWT
fi

if [ "$COLLECTOR_HOST" ] ; then
    echo "COLLECTOR_HOST = $COLLECTOR_HOST" >> /etc/condor/condor_config.local
fi

#Note the clientgroup will require quotation marks in the env variable
if [ "$CLIENTGROUP" ] ; then
    echo "CLIENTGROUP = $CLIENTGROUP >> /etc/condor/condor_config.local"
fi

# To keep docker partition from filling up
if [ "$DOCKER_SYSTEM_PRUNE" ] ; then
    docker system prune -a -fg
fi


#TODO Make nobody user able to run jobs
####################### HOST PATHS ############################################
DIRS_TO_CREATE=$(condor_config_val DIRS_TO_CREATE)
mkdir -p $DIRS_TO_CREATE
chmod 770 $DIRS_TO_CREATE && chown root:condor $DIRS_TO_CREATE
# /condor/execute root-squashed or not condor-owned: requiring world-writability
chmod 01777 $(condor_config_val EXECUTE)
chmod 01777 /var/run/docker.sock
/update-config
####################### HOST PATHS ############################################



# Ensure condor user can write to logs, since these are mounted onto host
chown condor $(condor_config_val log) $(condor_config_val lock) $(condor_config_val run)






/update-config
