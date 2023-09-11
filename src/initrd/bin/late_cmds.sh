#!/bin/sh -x

set -o errexit

echo "start late_cmds.sh"

SRC=/cdrom/src
TARGET=/target/

while getopts s:t: OPT
do
  case $OPT in
     s) SRC=${OPTARG} ;;
     t) TARGET=${OPTARG} ;;
  esac
done
cp ${SRC}/initrd/bin/in_target.sh ${TARGET}/tmp/


[ "x$(cat /sys/devices/virtual/dmi/id/product_name)" != "xTeraStation" ] && exit 0



cp ${SRC}/initrd/bin/micro-evtd ${TARGET}/usr/local/sbin/

cp ${SRC}/micon_boot.service ${TARGET}/etc/systemd/system/
cp ${SRC}/disp-lcd.sh ${TARGET}/usr/local/sbin/
cp ${SRC}/update-lcd.sh ${TARGET}/usr/local/sbin/
cp ${SRC}/set-led.sh ${TARGET}/usr/local/sbin/

cp ${SRC}/hotswap.service ${TARGET}/etc/systemd/system/
cp ${SRC}/update_boot.sh ${TARGET}/usr/local/sbin/
cp ${SRC}/hotswap_enable.sh ${TARGET}/usr/local/sbin/

cp ${SRC}/it8721.conf ${TARGET}/etc/sensors.d/

echo it87ts >> ${TARGET}/etc/modules
echo gpio-it87 >> ${TARGET}/etc/modules
echo gpio-ich >> ${TARGET}/etc/modules
echo pinctrl-dnv >> ${TARGET}/etc/modules
mkdir -p ${TARGET}/etc/initramfs/post-update.d/

echo "end late_cmds.sh"

exit 0
