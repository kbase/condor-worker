#!/opt/rh/rh-python36/root/usr/bin/python
import os
import subprocess
import sys
import docker
import pwd
import logging
import requests

logging.basicConfig(level=logging.INFO)

# Up one level for scratch
scratch = os.path.dirname(os.environ.get("SUBMIT_WORKDIR", "/mnt/awe/condor/condor_job_execute"))
# Endpoint

# TODO Fail if this variable is not defined for startD
endpoint = os.environ.get("SERVICE_ENDPOINT", None)

if endpoint is None:
    raise Exception("SERVICES_ENDPOINT is not defined")

services = {f"{endpoint}/auth": {},
            f"{endpoint}/njs_wrapper": {"method": "NarrativeJobService.status", "version": "1.1",
                                        "id": 1, "params": []},
            f"{endpoint}/catalog": {"method": "Catalog.status", "version": "1.1", "id": 1,
                                    "params": []},
            f"{endpoint}/ws": {"method": "Workspace.status", "version": "1.1", "id": 1,
                               "params": []},
            }

# Docker Cache
var_lib_docker = os.environ.get("DOCKER_CACHE", "/var/lib/docker/")

user = "nobody"


##TODO Report to nagios
##TODO Report Reason why it fails

def checkIfNobody():
    """

    :return:
    """
    name = pwd.getpwuid(os.getuid()).pw_name
    if name != "nobody":
        logging.error(f"{name} is not nobody user")
        sys.exit(1)


def testDockerSocket():
    """
    Check to see if the nobody user has access to the docker socket
    """
    dc = docker.from_env()
    if len(dc.containers.list()) < 1:
        logging.error(f"Can't access docker socket")
        sys.exit(1)


def testWriteable():
    """
    Check to see if /mnt/awe/condor is writeable
    """
    if not os.access(scratch, os.W_OK | os.X_OK):
        logging.error(f"Can't access {scratch}")
        sys.exit(2)


def enoughSpace(mount_point, percentage):
    """
    Check to see if point has enough space (how to do this without DF?)
    """
    cmd = "/bin/df " + mount_point + " | awk '{ print $5 }' | tail -1 | cut -f1 -d'%'"
    space = 0
    try:
        space = subprocess.check_output(cmd, shell=True).decode()
        if int(space) < percentage:
            return
        else:
            logging.error(f"Can't access {mount_point} or not enough space {space}")
            sys.exit(2)
    except Exception as e:
        logging.error(f"Can't access {mount_point} or not enough space {space}" + str(e))
        sys.exit(2)


def checkEndpoints():
    """

    :return:
    """
    for service in services:
        response = requests.post(url=service, json=services[service])
        if response.status_code != 200:
            logging.error(f"{service} is not available")
            sys.exit(2)
        # else:
        #     logging.info(response.content.decode("utf-8"))
        

if __name__ == '__main__':
    checkIfNobody()
    testDockerSocket()
    testWriteable()
    enoughSpace(scratch, 95)
    enoughSpace(var_lib_docker, 95)
    checkEndpoints()
