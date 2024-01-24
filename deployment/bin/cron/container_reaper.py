#!/miniconda/bin/python
"""
This script is automatically run by the condor cronjob periodically
in order to clean up containers > 7 days or running without a starter
Required env vars are
# CONTAINER_REAPER_ENDPOINTS - A comma separated list of EE2 endpoints to manage containers for
# DELETE_ABANDONED_CONTAINERS - Set to true to enable the container reaper
# SLACK_WEBHOOK_URL - The slack webhook url to send messages to
"""

import json
import os
import socket
import subprocess
from datetime import datetime, timedelta
from typing import Set

import docker
import requests
from docker.models.containers import Container


def send_slack_message(message: str):
    """
    :param message: Escaped Message to send to slack
    """
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", None)
    slack_data = {"text": message}
    requests.post(
        webhook_url,
        data=json.dumps(slack_data),
        headers={"Content-Type": "application/json"},
    )


def filter_containers_by_time(potential_containers, days=0, minutes=0):
    filtered_containers = []
    seven_days_ago = datetime.now() - timedelta(days=days, minutes=minutes)

    for old_container in potential_containers:
        # Do we need to catch the chance that there is no created attribute?
        created_time_str = old_container.attrs['Created'][:26]
        created_time = datetime.fromisoformat(created_time_str)
        if created_time <= seven_days_ago:
            filtered_containers.append(old_container)
    return filtered_containers


def get_running_time_message(container, title=""):
    image_name = container.attrs['Config']['Image']
    if "kbase" in image_name:
        image_name = image_name.split(":")[1]
    user_name = container.attrs['Config']['Labels'].get('user_name')

    total_running_time = datetime.now() - datetime.fromisoformat(container.attrs['Created'][:26])
    days = total_running_time.days
    hours = total_running_time.seconds // 3600

    formatted_running_time = f"{days}D:{hours}H"
    return f"{title}:{hostname} {image_name}:{user_name}:{formatted_running_time}"


def reap_containers_running_more_than_7_days(potential_containers: Set[Container]):
    old_containers = filter_containers_by_time(potential_containers, days=7)

    if old_containers:
        for old_container in old_containers:
            message = get_running_time_message(old_container, title="reaper7daylimit")
            send_slack_message(message)
            try:
                container.stop()
                container.remove()
            except Exception as e:
                send_slack_message(f"Error removing container: {message}")


def reap_containers_when_there_is_no_starter(potential_containers: Set[Container]):
    """
    This function will reap containers that are running but have no starter, and have been running for 30 mins
    """

    condor_starter = check_for_condor_starter()
    if condor_starter:
        return

    runaway_containers = filter_containers_by_time(potential_containers, minutes=30)
    if runaway_containers:
        for runaway_container in runaway_containers:
            message = get_running_time_message(runaway_container, title="reaper_no_starter")
            send_slack_message(message)
            try:
                container.stop()
                container.remove()
            except Exception as e:
                send_slack_message(f"Error removing container: {message}")


def check_for_condor_starter():
    result = subprocess.run("ps -ef | grep '[c]ondor_starter'", shell=True, stdout=subprocess.PIPE, text=True)
    count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    return count > 0


if __name__ == "__main__":
    """
    PDSH_SSH_ARGS_APPEND="-o StrictHostKeyChecking=no -q" pdsh -w rancher@km[2-28]-p "docker ps | grep kbase| grep days" | sort -V |  grep -v worker
    """

    CONTAINER_REAPER_ENDPOINTS = os.environ.get("CONTAINER_REAPER_ENDPOINTS", "").split(",")
    DELETE_ABANDONED_CONTAINERS = os.environ.get("DELETE_ABANDONED_CONTAINERS", "false").lower() == "true"

    if not DELETE_ABANDONED_CONTAINERS:
        exit("DELETE_ABANDONED_CONTAINERS is not set to true")
    if not CONTAINER_REAPER_ENDPOINTS or CONTAINER_REAPER_ENDPOINTS == [""]:
        exit("No CONTAINER_REAPER_ENDPOINTS set, unsure where to manage containers")

    hostname = socket.gethostname()
    dc = docker.from_env()

    # Define the filters to specify that you are searching for only your specific containers in a multi worker environment
    # Also add user_name as a filter to make sure you aren't killing containers that happen to have EE2_ENDPOINT set,
    # The chances of EE2_endpoint and user_name as labels on a container should be very small.
    # CONTAINER_REAPER_ENDPOINTS = ["https://kbase.us/services/ee2", "https://appdev.kbase.us/services/ee2", "https://services.kbase.us/services/ee2/"]
    unique_containers = set()
    filters = {}
    for endpoint in CONTAINER_REAPER_ENDPOINTS:

        filters.update({
            "status": "running",
            "label": [
                f"ee2_endpoint={endpoint.strip()}",
                "user_name"
            ]
        })
        containers = dc.containers.list(filters=filters)
        for container in containers:
            unique_containers.add(container)

    reap_containers_running_more_than_7_days(potential_containers=unique_containers)
    reap_containers_when_there_is_no_starter(potential_containers=unique_containers)
