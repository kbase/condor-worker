FROM htcondor/execute:lts-el8
ENV container docker

# Ge$t commonly used utilities
RUN yum -y update && yum upgrade -y 
RUN yum install -y drpm
RUN yum -y install -y epel-release wget which git gcc libcgroup libcgroup-tools stress-ng tmpwatch

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

#ADD DIRS
RUN mkdir -p /var/run/condor && mkdir -p /var/log/condor && mkdir -p /var/lock/condor && mkdir -p /var/lib/condor/execute

# Maybe you want: rm -rf /var/cache/yum, to also free up space taken by orphaned data from disabled or removed repos
RUN rm -rf /var/cache/yum

COPY --chown=kbase deployment/ /kb/deployment/

# Install dependencies for JobRunner ee2 branch. These might not match up with the other JobRunner branch
ENV PATH /miniconda/bin:$PATH
RUN /kb/deployment/bin/install_python_dependencies.sh

# The BUILD_DATE value seem to bust the docker cache when the timestamp changes, move to
# the end
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url="https://github.com/kbase/condor-worker.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0.0" \
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
