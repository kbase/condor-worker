#!/usr/bin/env python
# This script is used to find abandoned containers running on a condor worker.
# It requires a webhook URL environmental variable in order to send a notification to a slack channel
import json
import logging
import os
import subprocess
import time
import datetime
import requests

logging.basicConfig(level=logging.DEBUG)

# Improvements: Use a library

while (True):
    delete = os.environ.get('DELETE_ABANDONED_CONTAINERS')
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')

    hostname = subprocess.check_output('hostname').strip()
    logging.info("About to check for jobs on" + str(hostname))

    try:
        cmd = "docker ps | grep dockerhub | cut -f1 -d' '"
        running_containers = subprocess.check_output(cmd, shell=True, timeout=)

        container_ids = running_containers.split("\n")
        container_ids = filter(None, container_ids)

        cmd = 'ps -ax -o command | egrep "java -cp /mnt/awe/condor/.+/NJSWrapper-all.jar us.kbase.narrativejobservice.sdkjobs.SDKLocalMethodRunner" | grep -v grep | cut -f5 -d" "'
        java_procs = str(subprocess.check_output(cmd, shell=True))
        running_job_ids = java_procs.split("\n")

        running_job_ids = filter(None, running_job_ids)

        logging.info(running_job_ids)

        now = datetime.datetime.now()

        for container_id in container_ids:

            # Try catch here so the script can keep going
            try:
                cmd = "docker inspect --format '{{ index .Config.Labels \"job_id\"}}' " + str(
                    container_id)
                ujs_id = str(subprocess.check_output(cmd, shell=True).strip())
                cmd = "docker inspect --format '{{ index .Config.Labels \"condor_id\"}}' " + str(
                    container_id)
                condor_id = str(subprocess.check_output(cmd, shell=True).strip())

                #Skip containers without a condor or worker id
                if len(ujs_id) == 0 and len(condor_id) == 0:
                    continue

                if ujs_id not in running_job_ids:
                    message = "container:[{}] job_id:[{}] condor_id:[{}] is dead ({}) {} ".format(
                        container_id,
                        ujs_id,
                        condor_id,
                        hostname,
                        now)

                    slack_data = {'text': message}

                    response = requests.post(
                        webhook_url, data=json.dumps(slack_data),
                        headers={'Content-Type': 'application/json'}
                    )

                    if delete == "true":
                        cmd = 'docker stop {} && docker container rm -v {}'.format(container_id,
                                                                                   container_id)
                        logging.error(message)
                        logging.error(cmd)
                        output = subprocess.check_output(cmd, shell=True)

                        slack_data = {'text': 'docker rm output:' + str(output)}
                        response = requests.post(
                            webhook_url, data=json.dumps(slack_data),
                            headers={'Content-Type': 'application/json'}
                        )



                elif ujs_id in running_job_ids:
                    logging.info("Job still running: " + ujs_id)

            except Exception as e:
                print(e)

    except Exception as e:
        print(e)

    time.sleep(60)
