# Condor-worker requirements


The condor workers require 
* `/sys/fs/cgroup:/sys/fs/cgroup` mounted
* rngd service daemon running to generate entropy for starting up callback server [see gist](https://gist.github.com/bio-boris/3a6665fa8f2a8986e8a6ee606311a79e)
* `SET_NOBODY_USER_GUID = 999` (or the GID of the mounted dirs)
* `SET_NOBODY_USER_UID = 999` (or the UID of the mounted dirs)
* REFDATA Permissions set correctly
* Docker needs privileges to set cgroups/namespaces
* CLIENTGROUPS set with extra apostrophes

# Required Environmental Variables for the worker
* COLLECTOR_HOST
* CONDOR_HOST
* POOL_PASSWORD
* SCHEDD_HOST
* UID_DOMAIN
* USE_TCP
* SET_NOBODY_USER_GUID 
* SET_NOBODY_USER_UID
* CONDOR_SUBMIT_WORKDIR
* EXECUTE_SUFFIX
* EE2_ENDPOINT
* SERVICE_ENDPOINT
* DOCKER_CACHE
* CGROUP_MEMORY_LIMIT_POLICY
* USE_POOL_PASSWORD=yes

## HTCondor STARTD_CRON Environment Variables

* The cronjobs pass their environmental variables to the scripts they run.
* You can check the condor start log for their status and output when something goes wrong.
* You won't know if the cronjob is running unless you check the condor start log for a missing env var or possibly a job is stuck in a NODE_IS_HEALTHY=false state
* If an env var is present in the cronjobs.config, it is required, otherwise the template engine won't render it
* Q: Why are they in both the cronjobs.config and ALSO in environmental vars section? A: I'm not sure. Need to look at that why https://github.com/kbase/condor-worker/issues/59


### NodeHealth Health Check

#### Required Environmental Variables
* SLACK_WEBHOOK_URL  (dev or prod channels)
* SERVICE_ENDPOINT, e.g. https://kbase.us/services/ee2

#### Optional Environmental Variables
* DOCKER_CACHE (default: /var/lib/docker/)
* CONDOR_SUBMIT_WORKDIR (default: /cdr)
* EXECUTE_SUFFIX (default: "")
* CHECK_CONDOR_STARTER_HEALTH (default: true)
* DEBUG (default: false)
* CHECK_CONDOR_STARTER_HEALTH (default: true)

### DeleteExitedContainers
#### Required Environmental Variables
* SLACK_WEBHOOK_URL (dev or prod channels)


### EE2ContainerREAPER
#### Required Environmental Variables
* SLACK_WEBHOOK_URL (dev or prod channels)
* CONTAINER_REAPER_ENDPOINTS, e.g. https://kbase.us/services/ee2,https://services.kbase.us/services/ee2,
* DELETE_ABANDONED_CONTAINERS required to be set to true

