#!/usr/bin/env bash
# Usage - chmod +x
# ./remove_exited_containers.sh
# Sends a message about the containers you are going to delete on the host you run this on


#ee_notifications channel
webhook_url=${SLACK_WEBHOOK_URL}

hostname=`hostname`

# This will avoid inadvertently removing any containers which happen to have
# the word Exit in the name or command, and won't stop working if the output format of "docker ps -a" ever changes.

exited_containers=`docker ps -a --filter status=exited --format {{.ID}}`
n=`docker ps -a --filter status=exited --format {{.ID}} | wc -l`
message="Deleting $n exiting containers from $hostname"

# This cannot remove running containers
if [[ ${n} > 0 ]];
then
    `echo $exited_containers | xargs docker rm`
	curl -X POST -H 'Content-type: application/json' --data "{'text':'${message}'}" $webhook_url
fi
