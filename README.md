# Condor-worker requirements


The condor workers require 
* `/sys/fs/cgroup:/sys/fs/cgroup` mounted
* rngd service daemon running to generate entropy for starting up callback server [see gist](https://gist.github.com/bio-boris/3a6665fa8f2a8986e8a6ee606311a79e)
* `SET_NOBODY_USER_GUID = 999` (or the GID of the mounted dirs)
* `SET_NOBODY_USER_UID = 999` (or the UID of the mounted dirs)
* REFDATA Permissions set correctly
* Docker needs privileges to set cgroups/namespaces
* CLIENTGROUPS set with extra apostrophes

# Required Environmental Variables
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

* DELETE_ABANDONED_CONTAINERS
* EE2_ENDPOINT
* SERVICE_ENDPOINT
* DOCKER_CACHE
* CGROUP_MEMORY_LIMIT_POLICY
* USE_POOL_PASSWORD=yes

## HTCondor `STARTD_CRON` Environment Variables

1. **SLACK_WEBHOOK_URL**
   - Used in: `NodeHealth`, `DeleteExitedContainers`, `EE2ContainerREAPER`, `EE2ContainerREAPER2` 
   - Don't forget to set one for dev and prod differently

2. **SERVICE_ENDPOINT**
   - Used in: `NodeHealth`, `EE2ContainerREAPER`.

3. **CONDOR_SUBMIT_WORKDIR**
   - Used in: `NodeHealth`, `EE2ContainerREAPER`, `ManageCondorSubmitWorkdir`.

4. **DOCKER_CACHE**
   - Used in: `NodeHealth`, `EE2ContainerREAPER`.

5. **DELETE_ABANDONED_CONTAINERS**
   - Used in: `NodeHealth`, `EE2ContainerREAPER`.

6. **EE2_ENDPOINT**
   - Used in: `EE2ContainerREAPER`.

7. **CONTAINER_REAPER_ENDPOINTS**
   - Used in: `EE2ContainerREAPER2` 

8. **CONDOR_SUBMIT_WORKDIR** (repeated)
   - Used in: `ManageCondorSubmitWorkdir`.