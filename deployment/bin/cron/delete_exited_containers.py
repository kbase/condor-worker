#!/miniconda/bin/python
import os
import json
import requests
import docker
import socket
import datetime


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


if __name__ == "__main__":
    # send_slack_message(f"Job DELETE_EXITED is beginning at {datetime.datetime.now()}")
    hostname = socket.gethostname()
    dc = docker.from_env()
    ec = dc.containers.list(filters={"status": "exited"})
    count = len(ec)

    if count > 0:
        dc.containers.prune()
        send_slack_message(f"Deleted {count} stopped containers on {hostname}")

    # send_slack_message(f"Job DELETE_EXITED is ENDING at {datetime.datetime.now()}")
