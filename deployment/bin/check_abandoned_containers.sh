#!/usr/bin/env bash
#This script is used to find abandoned containers running on a condor worker.
#It requires a webhook URL environmental variable in order to send a notification to a slack channel

while true
do
    hostname=`hostname`
    webhook_url=${SLACK_WEBHOOK_URL}
    running="2"
    running_containers=`docker ps | grep dockerhub | cut -f1 -d' '`
    for container_id in ${running_containers}
    do
        condor_id=`docker inspect ${container_id} | grep condor_id | egrep -o "[0-9]+\.[0-9]"`
        last_job_status=`condor_q ${condor_id} -attributes JobStatus -long | egrep -o "[0-9]"`
        remote_host=`condor_q ${condor_id} -attributes RemoteHost -long | cut -f2 -d'='`
        last_remote_host=`condor_q ${condor_id} -attributes LastRemoteHost -long | cut -f2 -d'='`

        if [[ ${last_job_status} = 2 ]];
        then
            message="container_id ${condor_id} ${last_job_status} ${remote_host} ${last_remote_host} running"
        else
            message="DOCKER_ID:${container_id} CONDOR_ID:${condor_id} STATUS:${last_job_status} HOST:${remote_host} ${last_remote_host} (${hostname}) container is abandoned"
            curl -X POST -H 'Content-type: application/json' --data "{'text':'${message}'}" $webhook_url
            #docker stop $container && docker container rm -v $container
        fi
    done
sleep 60
done
