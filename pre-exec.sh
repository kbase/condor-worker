#!/bin/bash

# See documentation at https://github.com/htcondor/htcondor/tree/main/build/docker/services#providing-additional-configuration


if [ "$CONDOR_JWT_TOKEN" ] ; then
    echo "$CONDOR_JWT_TOKEN" > /etc/condor/tokens.d/JWT
    chmod 600 /etc/condor/tokens.d/JWT
fi

if [ "$COLLECTOR_HOST" ] ; then
    echo "COLLECTOR_HOST = $COLLECTOR_HOST" >> /etc/condor/condor_config.local
    /update-config
fi
