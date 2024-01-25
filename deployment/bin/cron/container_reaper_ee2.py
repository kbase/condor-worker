# #!/miniconda/bin/python
# import datetime
# import json
# import logging
# import os
# import socket
# from typing import List, Dict
#
# import docker
# import psutil
# import requests
# from docker.models.containers import Container
#
# # REQUIRED ENVIRONMENT VARIABLES
# ee2_endpoint_url = os.environ.get("EE2_ENDPOINT")
# if not ee2_endpoint_url:
#     raise Exception("EE2 Endpoint not set")
#
# webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
# if not webhook_url:
#     raise Exception("SLACK_WEBHOOK_URL is not defined")
#
# # OPTIONAL ENVIRONMENT VARIABLES
# kill = os.environ.get("DELETE_ABANDONED_CONTAINERS", "false").lower() == "true"
#
# logging.basicConfig(level=logging.INFO)
# hostname = socket.gethostname()
# dc = docker.from_env()
#
#
# def find_dockerhub_jobs() -> Dict:
#     try:
#         all_containers = dc.containers
#         container_list = all_containers.list()
#     except Exception as e:
#         send_slack_message(str(e) + hostname)
#         raise e
#
#     job_containers = {}
#
#     for container in container_list:
#         cnt_id = container.id
#         try:
#             cnt = all_containers.get(cnt_id)
#             labels = cnt.labels
#             label_keys = labels.keys()
#             if (
#                     "condor_id" in label_keys
#                     and "ee2_endpoint" in label_keys
#                     and "worker_hostname" in label_keys
#             ):
#                 if (
#                         labels.get("worker_hostname") == hostname
#                         and labels.get("ee2_endpoint") == ee2_endpoint_url
#                 ):
#                     labels["image"] = cnt.image
#                     job_containers[cnt_id] = labels
#         except Exception as e:
#             logging.error(f"Container {cnt_id} doesn't exist anymore")
#             logging.error(e)
#
#     return job_containers
#
#
# def find_running_jobs():
#     """
#     Return a list of job ids from running job processes.
#     Since python procs have multiple entries, keep only 1 version
#     """
#
#     # send_slack_message(f"Job CONTAINER_REAPER is FINDING RUNNING JOBS at {datetime.datetime.now()}")
#     ls = []
#     for p in psutil.process_iter(attrs=["name", "cmdline"]):
#         if (
#                 "/miniconda/bin/python" in p.info["cmdline"]
#                 and "./jobrunner.py" in p.info["cmdline"]
#         ):
#             ls.append(p.info["cmdline"][-2])
#     return list(set(ls))
#
#
# def send_slack_message(message: str):
#     """
#
#     :param message: Escaped Message to send to slack
#     :return:
#     """
#
#     slack_data = {"text": message}
#     requests.post(
#         webhook_url,
#         data=json.dumps(slack_data),
#         headers={"Content-Type": "application/json"},
#     )
#
#
# def notify_slack(cnt_id: str, labels: dict(), running_job_ids: List):
#     now = datetime.datetime.now()
#
#     job_id = labels.get("job_id", None)
#     # app_id = labels['app_id']
#     app_name = labels.get("app_name", None)
#     method_name = labels.get("method_name", None)
#     condor_id = labels.get("condor_id", None)
#     username = labels.get("user_name", None)
#
#     msg = f"cnt_id:{cnt_id} job_id:{job_id} condor_id:{condor_id} for {username} not in running_job_ids {running_job_ids} ({now}) hostname:({hostname}) app:{app_name} method:{method_name} (kill = {kill}) "
#     send_slack_message(msg)
#
#
# def kill_docker_container(cnt_id: str):
#     """
#     Kill a docker container. The job finish script should clean up after itself.
#     :param cnt_id: The container to kill/remove
#     """
#     if kill is True:
#         cnt = dc.containers.get(cnt_id)  # type: Container
#         try:
#             cnt.kill()
#         except Exception:
#             try:
#                 cnt.remove(force=True)
#             except Exception:
#                 send_slack_message(f"Couldn't delete {cnt_id} on {hostname}")
#
#
# def kill_dead_jobs(running_jobs: List, docker_processes: Dict):
#     """
#     Check whether there are runaway docker containers
#     :param running_jobs:  A list of condor jobs gathered from the starter scripts
#     :param docker_processes: A list of docker containers
#     """
#     # send_slack_message(f"Job CONTAINER_REAPER is KILLING DEAD JOBS at {datetime.datetime.now()}")
#     for cnt_id in docker_processes:
#         labels = docker_processes[cnt_id]
#         job_id = labels.get("job_id", None)
#         if job_id not in running_jobs:
#             notify_slack(cnt_id, labels, running_jobs)
#             if kill is True:
#                 kill_docker_container(cnt_id)
#
#
# if __name__ == "__main__":
#     try:
#         # send_slack_message(f"Job CONTAINER_REAPER is beginning at {datetime.datetime.now()}")
#         locally_running_jobrunners = find_running_jobs()
#         docker_jobs = find_dockerhub_jobs()
#         kill_dead_jobs(locally_running_jobrunners, docker_jobs)
#         # send_slack_message(f"Job CONTAINER_REAPER is ENDING at {datetime.datetime.now()}")
#     except Exception as ev:
#         send_slack_message(f"FAILURE on {hostname}" + str(ev))
#         logging.error(str(ev))
