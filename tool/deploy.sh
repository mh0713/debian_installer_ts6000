#!/bin/bash

cd $(dirname $0)/../

# default
USER=user
PASS=password
VER="$(git tag | sort | tail -n 1)+"

while getopts i:u:p:v: OPT
do
  case $OPT in
     i) IP=${OPTARG} ;;
     u) USER=${OPTARG} ;;
     p) PASS=${OPTARG} ;;
     v) VER=${OPTARG} ;;
  esac
done

ARCHIVE=~/release/proxy-${VER}.tar.gz
TARGET=/tmp/proxy

git archive HEAD -o ${ARCHIVE}
ssh-copy-id ${USER}@${IP}
scp ${ARCHIVE} ${USER}@${IP}:/tmp/proxy.tar.gz
ssh -t ${USER}@${IP} "echo ${PASS} | sudo -S rm -rf ${TARGET}"
ssh ${USER}@${IP} mkdir -p ${TARGET}/ansible/inventory/
ssh ${USER}@${IP} tar xzf /tmp/proxy.tar.gz -C ${TARGET}
ssh -t ${USER}@${IP} sudo -S ${TARGET}/install.py
