import requests
import os
import json

def notify_kbase_slack(message: str):
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

