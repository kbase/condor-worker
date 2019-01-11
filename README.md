# condor-worker requirements


The condor workers require 
* `/sys/fs/cgroup:/sys/fs/cgroup` mounted
* rngd service daemon running to generate entropy for starting up callback server [see gist](https://gist.github.com/bio-boris/3a6665fa8f2a8986e8a6ee606311a79e)
* `SET_NOBODY_USER_GUID = 999` (or the GID of the mounted dirs)
* `SET_NOBODY_USER_UID = 999` (or the UID of the mounted dirs)
* REFDATA Permissions set correctly
* Docker needs privileges to set cgroups/namespaces
* CLIENTGROUPS set with extra apostrophes
