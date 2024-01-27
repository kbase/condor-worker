#!/usr/bin/env bash

# Meant to be called by /usr/bin/docker-init --

/kb/deployment/bin/dockerize \
-template /kb/deployment/conf/.templates/condor_config_worker.templ:/etc/condor/condor_config.local \
-template /kb/deployment/conf/.templates/cronjobs.config.templ:/etc/condor/config.d/cronjobs.config \
-timeout 120s \
-stdout /var/log/condor/ProcLog \
-stdout /var/log/condor/StartLog \
/kb/deployment/bin/start-condor.sh
