FROM htcondor/execute:lts-el8
ENV container docker

# Get commonly used utilities
RUN yum -y update && yum upgrade -y 
RUN yum install -y drpm
RUN yum -y install -y epel-release wget which git gcc libcgroup libcgroup-tools stress-ng tmpwatch procps


# Install docker binaries
RUN yum install -y yum-utils device-mapper-persistent-data lvm2 && yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo && yum install -y docker-ce


#Install Python3 and Libraries (source /root/miniconda/bin/activate)
RUN yum install -y bzip2 \
&& wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
&& bash ~/miniconda.sh -b -p /miniconda


ENV PATH="/miniconda/bin:${PATH}"

# Add kbase user and set up directories
RUN useradd -c "KBase user" -rd /kb/deployment/ -u 998 -s /bin/bash kbase && \
    mkdir -p /kb/deployment/bin && \
    chown -R kbase /kb/deployment

#INSTALL DOCKERIZE
RUN wget -N https://github.com/kbase/dockerize/raw/master/dockerize-linux-amd64-v0.6.1.tar.gz && tar xvzf dockerize-linux-amd64-v0.6.1.tar.gz && cp dockerize /kb/deployment/bin && rm dockerize*

# Also add the user to the groups that map to "docker" on Linux and "daemon" on Mac
RUN usermod -a -G 0 kbase && usermod -a -G 999 kbase

#ADD DIRS
RUN mkdir -p /var/run/condor && mkdir -p /var/log/condor && mkdir -p /var/lock/condor && mkdir -p /var/lib/condor/execute

# Maybe you want: rm -rf /var/cache/yum, to also free up space taken by orphaned data from disabled or removed repos
RUN rm -rf /var/cache/yum



# The BUILD_DATE value seem to bust the docker cache when the timestamp changes, move to
# the end
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url="https://github.com/kbase/condor-worker.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0.0" \
      us.kbase.vcs-branch=$BRANCH \
      maintainer="Steve Chan sychan@lbl.gov"


ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini.asc /tini.asc
RUN gpg --batch --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 595E85A6B1B4779EA4DAAEC70B588DFF0527A9B7 \
 && gpg --batch --verify /tini.asc /tini
RUN chmod +x /tini && cp /tini /usr/bin/docker-init

# Delete un-needed-configs from htcondor/execute:lts-el8
# Revisit this when we change dockerize and token auth
RUN rm -f /etc/condor/config.d/00-htcondor-9.0.config
RUN rm -f /etc/condor/config.d/01-*


COPY --chown=kbase deployment/ /kb/deployment/
RUN /kb/deployment/bin/install_python_dependencies.sh

ENTRYPOINT [ "/usr/bin/docker-init" ]
CMD ["/kb/deployment/bin/docker-init.sh"]
WORKDIR /kb/deployment/jettybase
