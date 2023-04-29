#!/bin/bash

SECONDS=1800
ROTATES=16
PCAP_DIR="/mnt/array1/pcap"
CAPTURE_IF=enp8s0f1
HOSTNAME=$(hostname -s)

while getopts i:h:r:s: OPT
do
  case $OPT in
    i) CAPTURE_IF=$OPTARG;;
    h) HOSTNAME=$OPTARG;;
    r) ROTATES=$OPTARG;; 
    s) SECONDS=$OPTARG;;
  esac
done

/usr/sbin/tcpdump -i ${CAPTURE_IF} -nn -s 0 -G ${SECONDS} -W ${ROTATES} -w ${PCAP_DIR}/${HOSTNAME}-%Y%m%d-%H%M%S.pcap

exit 0