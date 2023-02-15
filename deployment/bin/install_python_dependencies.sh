#!/usr/bin/env bash

#Install Python3 Libraries
#TODO Requirements.txt
source /miniconda/bin/activate
pip install requests docker slackclient htcondor psutil lockfile
pip install sanic==21.9.3 docker==3.6.0

