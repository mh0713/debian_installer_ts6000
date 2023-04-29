#!/bin/bash

PCAP_DIR="pcap/"
PCAP_DONE_DIR="pcap_done/"
CSV_DIR="csv/"

while getopts i:o:d: OPT
do
  case $OPT in
     i) PCAP_DIR=$OPTARG;;
     o) CSV_DIR=$OPTARG;;
     d) PCAP_DONE_DIR=$OPTARG;;
  esac
done

find ${PCAP_DIR}/ -maxdepth 1 -type f -name '*.pcap' -printf '%f\n' | xargs -i sh -c "pcap2csv.py -i ${PCAP_DIR}/{} -o ${CSV_DIR}/{}.csv && mv ${PCAP_DIR}/{} ${PCAP_DONE_DIR}/ && gzip ${CSV_DIR}/{}.csv"
