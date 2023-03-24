#!/bin/bash

SOCKETS=$(fgrep 'physical id' /proc/cpuinfo | sort -u | wc -l)

if [ ${SOCKETS} -eq 0 ]; then
    ALL_CORES=$(nproc)
else
    CORES=$(fgrep 'cpu cores' /proc/cpuinfo | sort -u | sed 's/.*: //')
    ALL_CORES=$(( ${SOCKETS} * ${CORES} ))
fi

echo ${ALL_CORES}