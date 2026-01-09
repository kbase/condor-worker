FROM htcondor/base:25.0.1-el9

# Get commonly used utilities
RUN yum -y update && yum update -y systemd && yum -y install -y epel-release wget which git gcc stress-ng tmpwatch bzip2

# Install docker binaries 
RUN yum install -y yum-utils device-mapper-persistent-data lvm2 && yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo && yum install -y docker-ce


RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
&& bash ~/miniconda.sh -b -p /miniconda \
&& export PATH="/miniconda/bin:$PATH"

# Add kbase user and set up directories
RUN useradd -c "KBase user" -rd /kb/deployment/ -u 1000 -s /bin/bash kbase && \
    mkdir -p /kb/deployment/bin && \
    mkdir -p /kb/deployment/jettybase/logs/ && \
    touch /kb/deployment/jettybase/logs/request.log && \
    chown -R kbase /kb/deployment

#INSTALL DOCKERIZE
RUN wget -N https://github.com/kbase/dockerize/raw/master/dockerize-linux-amd64-v0.6.1.tar.gz && tar xvzf dockerize-linux-amd64-v0.6.1.tar.gz && cp dockerize /kb/deployment/bin && rm dockerize*




#ADD DIRS
RUN mkdir -p /var/run/condor && mkdir -p /var/log/condor && mkdir -p /var/lock/condor && mkdir -p /var/lib/condor/execute

# Maybe you want: rm -rf /var/cache/yum, to also free up space taken by orphaned data from disabled or removed repos
RUN rm -rf /var/cache/yum

ENV PATH=/miniconda/bin:$PATH


RUN pip install uv requests websockets==10.0 slackclient psutil sanic==21.12.2 docker==7.1.0 


COPY --chown=kbase deployment/ /kb/deployment/


ENV KB_DEPLOYMENT_CONFIG=/kb/deployment/conf/deployment.cfg


ENTRYPOINT [ "/kb/deployment/bin/dockerize" ]
CMD [ "-template", "/kb/deployment/conf/.templates/deployment.cfg.templ:/kb/deployment/conf/deployment.cfg", \
      "-template", "/kb/deployment/conf/.templates/http.ini.templ:/kb/deployment/jettybase/start.d/http.ini", \
      "-template", "/kb/deployment/conf/.templates/server.ini.templ:/kb/deployment/jettybase/start.d/server.ini", \
      "-template", "/kb/deployment/conf/.templates/start_server.sh.templ:/kb/deployment/bin/start_server.sh", \
      "-template", "/kb/deployment/conf/.templates/condor_config.templ:/etc/condor/condor_config.local", \
      "-stdout", "/kb/deployment/jettybase/logs/request.log", \
      "/kb/deployment/bin/start_server.sh" ]

WORKDIR /kb/deployment/jettybase
