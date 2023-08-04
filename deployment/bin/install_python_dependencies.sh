#!/usr/bin/env bash

#Install Python3 Libraries for cronjobs and for job runner

source /miniconda/bin/activate
pip install requests==2.29.0
pip install docker==6.1.3
pip install slackclient==2.9.4
pip install htcondor==10.7.0
pip install psutil==5.9.5
pip install lockfile==0.12.2
pip install sanic==21.9.3
