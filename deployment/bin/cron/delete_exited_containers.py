#!/miniconda/bin/python
# This script is automatically run by the condor cronjob periodically
# in order to clean up exited docker containers.
import json
import os
import socket

import docker
import requests


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


if __name__ == "__main__":
    hostname = socket.gethostname()
    dc = docker.from_env()
    ec = dc.containers.list(filters={"status": "exited"})
    kbase_containers = [c for c in ec if "kbase" in c.attrs["Config"]["Image"]]
    container_image_names = [c.attrs["Config"]["Image"] for c in kbase_containers]
    if kbase_containers:
        for container in kbase_containers:
            container.remove()
        debug_mode = os.environ.get("DEBUG", "false").lower() == "true"
        if debug_mode:
            send_slack_message(
                f"Deleted {len(kbase_containers)} `exited` containers with 'kbase' in image name on {hostname}: {container_image_names}")
