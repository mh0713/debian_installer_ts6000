#!/bin/bash -x

cd $(dirname $0)/proxy/

while getopts h:v: OPT
do
  case $OPT in
     h) HOST=${OPTARG} ;;
     v) VER=${OPTARG} ;;
  esac
done

ARCHIVE=~/release/proxy-${VER}.tar.gz
TARGET=/tmp/proxy

git archive HEAD -o ${ARCHIVE}
scp ${ARCHIVE} ${HOST}:/tmp/proxy.tar.gz
ssh -t ${HOST} sudo rm -rf ${TARGET}
ssh ${HOST} mkdir -p ${TARGET}/ansible/inventory/
ssh ${HOST} tar xzvf /tmp/proxy.tar.gz -C ${TARGET}
ssh -t ${HOST} sudo ${TARGET}/install.py --hostname ${HOST}
