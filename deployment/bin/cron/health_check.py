#!/opt/rh/rh-python36/root/usr/bin/python
import os
import subprocess
import sys
import docker
import pwd
import logging
import requests
import json
import socket
import pwd
import stat
import datetime


def send_slack_message(message):
    """
    :param message: Escaped Message to send to slack
    """
    # ee_notifications_channel
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", None)
    slack_data = {'text': message}
    requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )


# Up one level for scratch
scratch = os.path.dirname(
    os.environ.get("CONDOR_SUBMIT_WORKDIR", "/mnt/awe/condor/condor_job_execute"))
# Endpoint

endpoint = os.environ.get("SERVICE_ENDPOINT", None)

if endpoint is None:
    raise Exception("SERVICE_ENDPOINT is not defined")

# Docker Cache
var_lib_docker = os.environ.get("DOCKER_CACHE", "/var/lib/docker/")

user = "nobody"
pid = pwd.getpwnam(user).pw_uid


# TODO Report to nagios

def exit(message):
    print("NODE_IS_HEALTHY = False")
    print(f"HEALTH_STATUS_MESSAGE = '{message}'")
    print("- update:true")
    now = datetime.datetime.now()
    send_slack_message(f"Ran healthcheck at {now} on {socket.gethostname()} with failure: " + message)
    sys.exit(1)


def exit_successfully():
    print("NODE_IS_HEALTHY = True")
    print(f"HEALTH_STATUS_MESSAGE = Healthy {datetime.datetime.now()}")
    print("- update:true")
    sys.exit(0)


def checkIfNobody():
    name = pwd.getpwuid(os.getuid()).pw_name
    if name != "nobody":
        message = f"{name} is not nobody user"
        logging.error(message)
        exit(message)


def testDockerOld():
    """
    Check to see if the nobody user has access to the docker socket
    """
    dc = docker.from_env()
    if len(dc.containers.list()) < 1:
        message = f"Cannot access docker socket"
        logging.error(message)
        exit(message)


def testWriteableOld():
    """
    Check to see if /mnt/awe/condor is writeable
    """
    if not os.access(scratch, os.W_OK | os.X_OK):
        message = f"Cannot  access {scratch}"
        logging.error(message)
        exit(message)


def testDockerSocket():
    """
    Check to see if the nobody user has access to the docker socket
    """
    socket = "/var/run/docker.sock"
    if os.stat(socket).st_gid != pid:
        message = f"Cannot access docker socket"
        logging.error(message)
        exit(message)


def testWorldWriteable():
    """
    Check to see if /mnt/awe/condor is writeable
    """
    # Strip out octal 0o
    perms = str(oct(stat.S_IMODE(os.stat(scratch).st_mode))).lstrip("0").lstrip("o")

    if perms == '01777' or perms == '1777' or perms == "0o1777":
        return
    else:
        message = f"Cannot access {scratch} gid={ os.stat(scratch).st_gid } perms={perms}"
        logging.error(message)
        exit(message)


def enoughSpace(mount_point, nickname, percentage):
    """
    Check to see if point has enough space (how to do this without DF?)
    """
    cmd = "/bin/df " + mount_point + " | awk '{ print $5 }' | tail -1 | cut -f1 -d'%'"
    usage = 0

    try:
        usage = subprocess.check_output(cmd, shell=True).decode().strip()
        if int(usage) < percentage:
            # send_slack_message(
            #     f"The amount of usage  {usage}  for {mount_point} ({nickname}) which is less than  {percentage}")
            return
        else:
            message = f"Can't access {mount_point} or not enough space ({usage} > {percentage})"
            logging.error(message)
            exit(message)
    except Exception as e:
        message = f"Can't access {mount_point} or not enough space {usage}" + str(e)
        logging.error(message)
        exit(message)


def checkEndpoints():
    """
    Check auth/njs/catalog/ws
    """

    services = {f"{endpoint}/auth": {},
                f"{endpoint}/njs_wrapper": {"method": "NarrativeJobService.status",
                                            "version": "1.1",
                                            "id": 1, "params": []},
                f"{endpoint}/catalog": {"method": "Catalog.status", "version": "1.1", "id": 1,
                                        "params": []},
                f"{endpoint}/ws": {"method": "Workspace.status", "version": "1.1", "id": 1,
                                   "params": []},
                }

    for service in services:
        response = requests.post(url=service, json=services[service])
        if response.status_code != 200:
            message = f"{service} is not available"
            logging.error(message)
            exit(message)


if __name__ == '__main__':
    try:
        testDockerSocket()
        testWorldWriteable()
        enoughSpace(scratch, "scratch", 95)
        enoughSpace(var_lib_docker, "docker", 95)
        checkEndpoints()
    except Exception as e:
        exit(str(e))
    exit_successfully()
