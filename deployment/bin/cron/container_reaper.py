#!/opt/rh/rh-python36/root/usr/bin/python
import datetime
import fnmatch
import json
import logging
import os
import socket

import docker
import psutil
import requests
from clients.NarrativeJobServiceClient import NarrativeJobService

slack_key = os.environ.get("SLACK_WEBHOOK_KEY", None)
# ee_notifications_channel
webhook_url = os.environ.get("SLACK_WEBHOOK_URL", None)

kill = os.environ.get("DELETE_ABANDONED_CONTAINERS", "false")
if kill.lower() == "true":
    kill = True
else:
    kill = False

njs_endpoint_url = os.environ.get("NJS_ENDPOINT", None)

if njs_endpoint_url is None:
    raise Exception("NJS Endpoint not set")

hostname = socket.gethostname()
dc = docker.from_env()


def find_dockerhub_jobs() -> dict():
    all_containers = dc.containers
    list = all_containers.list()

    job_containers = {}

    for container in list:
        cnt_id = container.id
        try:
            cnt = all_containers.get(cnt_id)
            labels = cnt.labels
            if 'condor_id' in labels.keys() and 'njs_endpoint' in labels.keys():
                labels['image'] = cnt.image
                job_containers[cnt_id] = labels
        except Exception as e:
            logging.error(f"Container {cnt_id} doesn't exist anymore")
            logging.error(e)

    return job_containers


def find_running_jobs(name):
    "Return a list of processes matching 'name'."
    ls = []
    for p in psutil.process_iter(attrs=['name', 'cmdline']):
        if name in p.info['cmdline']:
            ls.append(p.info['cmdline'][-2])
    return ls


def send_slack_message(message):
    """

    :param message: Escaped Message to send to slack
    :return:
    """

    slack_data = {'text': message}
    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )


def notify_slack(cnt_id, labels, running_job_ids):
    now = datetime.datetime.now()

    job_id = labels.get('job_id', None)
    # app_id = labels['app_id']
    app_name = labels.get('app_name', None)
    method_name = labels.get('method_name', None)
    condor_id = labels.get('condor_id', None)
    username = labels.get('user_name', None)

    msg = f"cnt_id:{cnt_id} job_id:{job_id} condor_id:{condor_id} for {username} not in running_job_ids {running_job_ids} ({now}) hostname:({hostname}) app:{app_name} method:{method_name} (kill = {kill}) "
    send_slack_message(msg)


# @deprecated for EVENTLOG
def notify_user(cnt_id, labels):
    username = labels.get('user_name', None)
    job_id = labels.get('job_id', None)
    # TODO add this to a configuration somewhere or ENV variable
    job_directory = f"/mnt/awe/condor/{username}/{job_id}"

    print("About to notify")
    print(labels)

    env_files = []
    for file in os.listdir(job_directory):
        if fnmatch.fnmatch(file, 'env_*'):
            env_files.append(file)

    print(env_files)
    env_filepath = env_files[0]
    if os.path.isfile(env_filepath):
        with open(env_filepath, 'r') as content_file:
            content = content_file.readlines()

        token = None
        for line in content:
            if "KB_AUTH_TOKEN" in line:
                token = line.split("=")[1]

        if token:
            njs = NarrativeJobService(token=token, url=njs_endpoint_url)
            status = njs.check_job(job_id)
            print(status)


def kill_docker_container(cnt_id: str):
    if kill is True:
        cnt = dc.containers.get(cnt_id)
        cnt.kill()
    else:
        pass


def kill_dead_jobs(running_jobs, docker_processes):
    for cnt_id in docker_processes:
        labels = docker_processes[cnt_id]
        job_id = labels.get('job_id', None)
        if job_id not in running_jobs:
            if kill is True:
                kill_docker_container(cnt_id)
                notify_slack(cnt_id, labels, running_jobs)


if __name__ == '__main__':
    try:
        name = "us.kbase.narrativejobservice.sdkjobs.SDKLocalMethodRunner"
        running_java_jobs = find_running_jobs(name)
        docker_jobs = find_dockerhub_jobs()
        kill_dead_jobs(running_java_jobs, docker_jobs)
    except Exception as e:
        send_slack_message("FAILURE" + str(e.with_traceback()))
        logging.error(e.with_traceback())
