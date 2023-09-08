#!/bin/bash

MICONAPL="/usr/local/sbin/micro-evtd -p /dev/ttyS0 -s3"

MODE=$1

if [ ${MODE} == "halt" ] || [ ${MODE} == "poweroff" ]; then
    ${MICONAPL} "SHUTDOWN"
else
    ${MICONAPL} "REBOOT"
fi

