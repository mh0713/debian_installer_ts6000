#!/bin/bash

PCAP_SRC="/mnt/array1/pcap"
PCAP_DEST="/home/user/pcap"
PORT=22
USER="user"

# -s {{ pcap_server }} -p {{ pcap_server_port }} -u {{ pcap_server_user }} -i {{ pcap_server_identity }}"

while getopts s:p:u:i: OPT
do
  case $OPT in
     s) SERVER=$OPTARG;;
     p) PORT=$OPTARG;;
     u) USER=$OPTARG;;
     i) IDENTITY=$OPTARG;;
  esac
done

for f in $(find ${PCAP_SRC} -type f -name *.pcap); do
  FNAME=$(basename $f)
  scp -P ${PORT} -i ${IDENTITY} ${f} ${USER}@${SERVER}:${PCAP_DEST}/ && rm -f ${f}
done

exit 0