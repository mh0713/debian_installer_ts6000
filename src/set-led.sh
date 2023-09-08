#!/bin/sh

MICONAPL="/usr/local/sbin/micro-evtd -p /dev/ttyS0 -s3"
LED_NO=$1
STATUS=$2

${MICONAPL} "LED_${STATUS} ${LED_NO}"
