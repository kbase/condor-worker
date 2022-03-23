# condor-worker requirements


The condor workers require 
* `/sys/fs/cgroup:/sys/fs/cgroup` mounted
* rngd service daemon running to generate entropy for starting up callback server [see gist](https://gist.github.com/bio-boris/3a6665fa8f2a8986e8a6ee606311a79e)
* `SET_NOBODY_USER_GUID = 999` (or the GID of the mounted dirs)
* `SET_NOBODY_USER_UID = 999` (or the UID of the mounted dirs)
* REFDATA Permissions set correctly
* Docker needs privileges to set cgroups/namespaces
* CLIENTGROUPS set with extra apostrophes

Environmental variables to be set in rancher
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
* SLACK_WEBHOOK_URL
* DELETE_ABANDONED_CONTAINERS
* NJS_ENDPOINT
* EE2_ENDPOINT
* SERVICE_ENDPOINT
* DOCKER_CACHE
* CGROUP_MEMORY_LIMIT_POLICY
* USE_POOL_PASSWORD=yes
