#!/bin/bash

DIR=$1

find ${DIR}/ -maxdepth 1 -type f -mtime +7 -name '*.pcap'  | xargs rm -f