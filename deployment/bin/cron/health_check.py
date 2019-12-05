#!/miniconda/bin/python
"""
This script is to be run by the condor cronjob periodically in order to test if the node is able to accept jobs or not.

"""
import datetime
import json
import logging
import os
import pwd
import socket
import stat
import subprocess
import sys

import docker
import psutil
import requests


def send_slack_message(message: str):
    """
    :param message: Escaped Message to send to slack
    """
    # ee_notifications_channel
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", None)
    slack_data = {"text": message}
    requests.post(
        webhook_url,
        data=json.dumps(slack_data),
        headers={"Content-Type": "application/json"},
    )


debug = False
scratch = os.environ.get("CONDOR_SUBMIT_WORKDIR", "/cdr")
scratch += os.environ.get("EXECUTE_SUFFIX", "")

# Endpoint

endpoint = os.environ.get("SERVICE_ENDPOINT", None)

if endpoint is None:
    exit("SERVICE_ENDPOINT is not defined")

# Docker Cache
var_lib_docker = os.environ.get("DOCKER_CACHE", "/var/lib/docker/")

user = "nobody"
pid = pwd.getpwnam(user).pw_uid
gid = pwd.getpwnam(user).pw_gid


# TODO Report to nagios


def exit_unsuccessfully(message: str):
    if debug is True:
        logging.error(message)

    print("NODE_IS_HEALTHY = False")
    print(f'HEALTH_STATUS_MESSAGE = "{message}"')
    print("- update:true")
    now = datetime.datetime.now()
    send_slack_message(
        f"POSSIBLE BLACK HOLE: Ran healthcheck at {now} on {socket.gethostname()} with failure: " + message
    )

    sys.exit(1)


def exit_successfully():
    print("NODE_IS_HEALTHY = True")
    print(f'HEALTH_STATUS_MESSAGE = "Healthy {datetime.datetime.now()}"')
    print("- update:true")
    sys.exit(0)


def check_if_nobody():
    name = pwd.getpwuid(os.getuid()).pw_name
    if name != "nobody":
        message = f"{name} is not nobody user"
        exit_unsuccessfully(message)


def test_free_memory():
    """
    Check to see if too much memory is being user. Maybe it's a runaway container?
    :return:
    """

    mem = psutil.virtual_memory()
    if mem.percent > 95:
        message = f"Memory usage is too high {mem}"
        exit_unsuccessfully(message)


def test_docker_socket():
    """
    Check to see if the nobody user has access to the docker socket
    """
    socket = "/var/run/docker.sock"
    socket_gid = os.stat(socket).st_gid

    # TODO FIX THIS TEST.. GROUPS ARE NOT BEING CORRECTLY SET INSIDE THE DOCKER CONTAINER
    gids = [999, 996, 995, 987]
    if socket_gid in gids:
        return

    message = f"Cannot access docker socket, check to make sure permissions of user in {gids}"
    exit_unsuccessfully(message)


def test_docker_socket2():
    """
    Check to see if the nobody user has access to the docker socket
    """
    dc = docker.from_env()
    if len(dc.containers.list()) < 1:
        message = f"Cannot access docker socket"
        exit_unsuccessfully(message)


def test_world_writeable():
    """
    Check to see if /mnt/awe/condor is writeable
    """
    # Strip out octal 0o
    perms = str(oct(stat.S_IMODE(os.stat(scratch).st_mode))).lstrip("0").lstrip("o")

    if perms == "01777" or perms == "1777" or perms == "0o1777":
        return
    else:
        message = (
            f"Cannot access {scratch} gid={os.stat(scratch).st_gid} perms={perms}"
        )
        exit_unsuccessfully(message)


def test_enough_space(mount_point, nickname, percentage):
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
            exit_unsuccessfully(message)
    except Exception as e:
        message = f"Can't access {mount_point} or not enough space {usage}" + str(e)
        exit_unsuccessfully(message)


def checkEndpoints():
    """
    Check auth/njs/catalog/ws
    """

    services = {
        f"{endpoint}/auth": {},
        f"{endpoint}/njs_wrapper": {
            "method": "NarrativeJobService.status",
            "version": "1.1",
            "id": 1,
            "params": [],
        },
        f"{endpoint}/catalog": {
            "method": "Catalog.status",
            "version": "1.1",
            "id": 1,
            "params": [],
        },
        f"{endpoint}/ws": {
            "method": "Workspace.status",
            "version": "1.1",
            "id": 1,
            "params": [],
        },
    }

    for service in services:
        response = requests.post(url=service, json=services[service], timeout=30)
        if response.status_code != 200:
            message = f"{service} is not available"
            exit_unsuccessfully(message)


def main():
    try:
        # send_slack_message(f"Job HEALTH_CHECK is beginning at {datetime.datetime.now()}")
        test_docker_socket()
        test_docker_socket2()
        test_world_writeable()
        test_enough_space(scratch, "scratch", 95)
        test_enough_space(var_lib_docker, "docker", 95)
        test_free_memory()
        checkEndpoints()
        # send_slack_message(f"Job HEALTH_CHECK is ENDING at {datetime.datetime.now()}")
    except Exception as e:
        exit_unsuccessfully(str(e))
    exit_successfully()


if __name__ == "__main__":
    main()
