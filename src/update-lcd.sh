#!/bin/bash

MICONAPL="/usr/local/sbin/micro-evtd -p /dev/ttyS0 -s3"

HOSTNAME=$(hostname)
IP=$(ip a show br0 | grep "inet "  | head -n 1 | awk '{print $2}')

${MICONAPL} "LCD_PUTS 0 ${HOSTNAME}"
${MICONAPL} "LCD_PUTS 1 ${IP%/*}"
