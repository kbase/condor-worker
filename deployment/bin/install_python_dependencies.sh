#!/usr/bin/env bash

#Install Python3 Libraries
#TODO Requirements.txt
source /miniconda/bin/activate
pip install requests docker slackclient htcondor psutil lockfile sanic==21.9.3
