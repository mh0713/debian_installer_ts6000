#!/bin/sh -x

echo "start late_cmds.sh"

# mount -t proc none /target/proc/
# mount -t sysfs none /target/sys/
cp /cdrom/src/*.sh /target/usr/local/bin/
cp /cdrom/src/bin/micro-evtd /target/usr/local/bin/
cp /cdrom/src/scripts/in_target.sh /target/tmp/

cp /cdrom/src/*.service /target/etc/systemd/system/
cp /cdrom/src/it8721.conf /target/etc/sensors.d/
cp -r /cdrom/src/micon_scripts /target/usr/local/bin/
cp /cdrom/src/micon_scripts/*.service /target/etc/systemd/system/
echo it87ts >> /target/etc/modules
echo gpio-it87 >> /target/etc/modules
echo gpio-ich >> /target/etc/modules
echo pinctrl-dnv >> /target/etc/modules
mkdir -p /target/etc/initramfs/post-update.d/

echo "end late_cmds.sh"

exit 0
