FROM centos:7
ENV container docker

# Add kbase user and set up directories
RUN useradd -c "KBase user" -rd /kb/deployment/ -u 998 -s /bin/bash kbase && \
    mkdir -p /kb/deployment/bin && \
    mkdir -p /kb/deployment/jettybase/logs/ && \
    touch /kb/deployment/jettybase/logs/request.log && \
    chown -R kbase /kb/deployment

# Get commonly used utilities
RUN yum -y update && yum -y install -y wget which git deltarpm && \
yum install -y java-1.8.0-openjdk java-1.8.0-openjdk-devel 


# Install Condor
RUN cd /etc/yum.repos.d && \
wget http://research.cs.wisc.edu/htcondor/yum/repo.d/htcondor-development-rhel7.repo && \
wget http://research.cs.wisc.edu/htcondor/yum/repo.d/htcondor-stable-rhel6.repo && \
wget http://research.cs.wisc.edu/htcondor/yum/RPM-GPG-KEY-HTCondor && \
rpm --import RPM-GPG-KEY-HTCondor && \
yum -y install condor.x86_64

# Mount for cgroups
VOLUME [ "/sys/fs/cgroup" ]

# These ARGs values are passed in via the docker build command
ARG BUILD_DATE
ARG VCS_REF
ARG BRANCH=develop


#INSTALL DOCKERIZE
RUN wget -N https://github.com/kbase/dockerize/raw/master/dockerize-linux-amd64-v0.6.1.tar.gz && tar xvzf dockerize-linux-amd64-v0.6.1.tar.gz && cp dockerize /kb/deployment/bin && rm dockerize*

# Install docker binaries (setsebool:  SELinux is disabled. libsemanage.semanage_commit_sandbox: Error while renaming /etc/selinux/targeted/active to /etc/selinux/targeted/previous. (Invalid cross-device link).)
RUN yum install -y yum-utils device-mapper-persistent-data lvm2 && yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo && yum install -y docker-ce
# Also add the user to the groups that map to "docker" on Linux and "daemon" on Mac
RUN usermod -a -G 0 kbase && usermod -a -G 999 kbase

# Maybe you want: rm -rf /var/cache/yum, to also free up space taken by orphaned data from disabled or removed repos
# RUN rm -rf /var/cache/yum

#ADD DIRS
RUN mkdir -p /var/run/condor && mkdir -p /var/log/condor && mkdir -p /var/lock/condor && mkdir -p /var/lib/condor/execute
#RUN touch /var/log/condor/StartLog /var/log/condor/ProcLog && chmod 778 /var/log/condor/* /var/lock/condor 
#RUN chown -R kbase:kbase /etc/condor /run/condor /var/lock/condor /var/log/condor /var/lib/condor/execute /var/log/condor/StartLog /var/log/condor/ProcLog

COPY --chown=kbase deployment/ /kb/deployment/


ENV KB_DEPLOYMENT_CONFIG /kb/deployment/conf/deployment.cfg

# The BUILD_DATE value seem to bust the docker cache when the timestamp changes, move to
# the end
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url="https://github.com/kbase/njs_wrapper.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0.0-rc1" \
      us.kbase.vcs-branch=$BRANCH \
      maintainer="Steve Chan sychan@lbl.gov"

ENTRYPOINT [ "/kb/deployment/bin/dockerize" ]
CMD [ "-template", "/kb/deployment/conf/.templates/deployment.cfg.templ:/kb/deployment/conf/deployment.cfg", \
      "-template", "/kb/deployment/conf/.templates/http.ini.templ:/kb/deployment/jettybase/start.d/http.ini", \
      "-template", "/kb/deployment/conf/.templates/server.ini.templ:/kb/deployment/jettybase/start.d/server.ini", \
      "-template", "/kb/deployment/conf/.templates/start_server.sh.templ:/kb/deployment/bin/start_server.sh", \
      "-template", "/kb/deployment/conf/.templates/condor_config.templ:/etc/condor/condor_config.local", \
      "-stdout", "/kb/deployment/jettybase/logs/request.log", \
      "/kb/deployment/bin/start_server.sh" ]

WORKDIR /kb/deployment/jettybase
