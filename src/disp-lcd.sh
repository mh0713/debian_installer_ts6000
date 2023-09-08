#!/bin/sh
MICONAPL='/usr/local/sbin/mico-evtd -p /dev/ttyS0 -s3'

${MICONAPL} "LCD_CLR"
${MICONAPL} "LCD_PUTS 0 $1"
sleep 5