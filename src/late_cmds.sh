#!/bin/sh -x

echo "start late_cmds.sh"

SRC=/cdrom/src

while getopts s: OPT
do
  case $OPT in
     s) SRC=${OPTARG} ;;
  esac
done

cp ${SRC}/micro-evtd /target/usr/local/sbin/

cp ${SRC}/micon_boot.service /target/etc/systemd/system/
cp ${SRC}/disp-lcd.sh /target/usr/local/sbin/
cp ${SRC}/update-lcd.sh /target/usr/local/sbin/
cp ${SRC}/set-led.sh /target/usr/local/sbin/

cp ${SRC}/hotswap.service /target/etc/systemd/system/
cp ${SRC}/update_boot.sh /target/usr/local/sbin/
cp ${SRC}/hostswap_enabe.sh /target/usr/local/sbin/

cp ${SRC}/it8721.conf /target/etc/sensors.d/

echo it87ts >> /target/etc/modules
echo gpio-it87 >> /target/etc/modules
echo gpio-ich >> /target/etc/modules
echo pinctrl-dnv >> /target/etc/modules
mkdir -p /target/etc/initramfs/post-update.d/

echo "end late_cmds.sh"

exit 0
