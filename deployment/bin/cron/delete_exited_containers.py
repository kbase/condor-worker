#!/miniconda/bin/python
# This script is automatically run by the condor cronjob periodically
# in order to clean up exited docker containers.
import os
import socket

import docker

from .send_slack_message import notify_kbase_slack

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
            notify_kbase_slack(
                f"Deleted {len(kbase_containers)} `exited` containers with 'kbase' in image name on {hostname}: {container_image_names}")
