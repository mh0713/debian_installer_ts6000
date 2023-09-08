#!/bin/bash -x
set -o errexit

echo "start in_target.sh"

SRC=/media/cdrom/src

while getopts s: OPT
do
  case $OPT in
     s) SRC=${OPTARG} ;;
  esac
done

echo "create symlinks"
ln -sf /usr/local/sbin/update_boot.sh /etc/initramfs/post-update.d/update_boot
ln -sf /usr/local/sbin/micon_shutdown.sh /lib/systemd/system-shutdown/micon_shutdown
ln -sf /usr/local/sbin/update-lcd /etc/NetworkManager/dispatcher.d/50-miconapl-lcd
systemctl enable hotswap.service
systemctl enable micon_boot.service

## do we need logic to ensure only the needed modules for a given device are installed?

echo "add modules"
modules="gpio_dnv gpio_it87 gpio_ich it87ts"

for mod in $modules
do
  cp -r "${SRC}/modules/$mod" "/usr/src/$mod-1.0/"
  dkms add -m "$mod" -v 1.0
done

echo "enable micon_boot.service"
systemctl enable micon_boot.service
udevadm trigger
/usr/local/sbin/update_boot.sh
exit 0