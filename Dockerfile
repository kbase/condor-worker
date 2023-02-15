FROM htcondor/execute:9.12.0-el7
ENV container docker

# See https://www-auth.cs.wisc.edu/lists/htcondor-users/2014-August/msg00044.shtml
COPY pre-exec.sh /root/config/pre-exec.sh
COPY kbase_worker.conf /etc/condor/condor_config.local

# Get commonly used utilities
RUN yum install -y deltarpm
RUN yum -y update && yum upgrade -y 
RUN yum -y install -y epel-release wget which git deltarpm gcc libcgroup libcgroup-tools stress-ng tmpwatch

# Install docker binaries 
RUN yum install -y yum-utils device-mapper-persistent-data lvm2 && yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo && yum install -y docker-ce

#Install Python3 and Libraries (source /root/miniconda/bin/activate)
RUN yum install -y bzip2 \
&& wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
&& bash ~/miniconda.sh -b -p /miniconda \
&& export PATH="/miniconda/bin:$PATH"

# Add kbase user and set up directories
RUN useradd -c "KBase user" -rd /kb/deployment/ -u 998 -s /bin/bash kbase && \
    mkdir -p /kb/deployment/bin && \
    mkdir -p /kb/deployment/jettybase/logs/ && \
    touch /kb/deployment/jettybase/logs/request.log && \
    chown -R kbase /kb/deployment

#INSTALL DOCKERIZE
RUN wget -N https://github.com/kbase/dockerize/raw/master/dockerize-linux-amd64-v0.6.1.tar.gz && tar xvzf dockerize-linux-amd64-v0.6.1.tar.gz && cp dockerize /kb/deployment/bin && rm dockerize*

# Also add the user to the groups that map to "docker" on Linux and "daemon" on Mac
RUN usermod -a -G 0 kbase && usermod -a -G 999 kbase

# Maybe you want: rm -rf /var/cache/yum, to also free up space taken by orphaned data from disabled or removed repos
RUN rm -rf /var/cache/yum

COPY --chown=kbase deployment/ /kb/deployment/

# Install dependencies for JobRunner
ENV PATH /miniconda/bin:$PATH
#RUN wget https://raw.githubusercontent.com/kbase/JobRunner/ee2/requirements.txt && pip install -r requirements.txt && rm requirements.txt
RUN /kb/deployment/bin/install_python_dependencies.sh

# The BUILD_DATE value seem to bust the docker cache when the timestamp changes, move to
# the end
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url="https://github.com/kbase/condor-worker.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0.0" \
      us.kbase.vcs-branch=$BRANCH \
      maintainer="Steve Chan sychan@lbl.gov"

WORKDIR /kb/deployment/jettybase
