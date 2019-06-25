#!/opt/rh/rh-python36/root/usr/bin/python
import os
import json
import requests
import docker
import socket


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

    hostname = socket.gethostname()
    dc = docker.from_env()
    ec = dc.containers.list(filters={"status": "exited"})
    count = len(ec)

    if count > 0:
        dc.containers.prune()
        send_slack_message(f"Deleted {count} stopped containers on {hostname}")
