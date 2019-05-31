#!/usr/bin/env bash

#Install Python3 Libraries
#TODO Requirements.txt
source /opt/rh/rh-python36/enable
pip install requests docker slackclient htcondor psutil
