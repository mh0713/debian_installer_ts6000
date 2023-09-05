#!/bin/bash

# フォルダ構成
#
# tmp
#   debian-files
#   img
#   iso
#   payload
#      source
#        examples
#        micon_scripts
#        modules
#


set -o errexit

distro="bookworm"

sudo apt update
sudo apt -y install gzip wget cpio syslinux isolinux xorriso mkisofs syslinux-utils

# cleanup working directory
rm -rf tmp/
mkdir -p tmp/{debian-files,payload/source,img,iso}

pushd tmp/debian-files
wget -N "https://deb.debian.org/debian/dists/$distro/main/installer-amd64/current/images/netboot/debian-installer/amd64/initrd.gz" 2>/dev/null
wget -N "https://deb.debian.org/debian/dists/$distro/main/installer-amd64/current/images/netboot/debian-installer/amd64/linux" 2>/dev/null
popd

cp install_scripts/preseed.cfg tmp/payload/
cp -r source/* tmp/payload/source/
cp -r installer_scripts tmp/payload/

gzip -dc tmp/debian-files/initrd.gz > tmp/initrd
if [ $? -ne 0 ]; then
        echo "failed to unpack initrd.gz, quitting"
        exit
fi
pushd tmp/payload
find . | cpio -v -H newc -o -A -F ../initrd
if [ $? -ne 0 ]; then
        echo "failed to patch initrd.gz, quitting"
        exit
fi
popd

xz --check=crc32 -z tmp/initrd
if [ $? -ne 0 ]; then
        echo "failed to pack initrd, quitting"
        exit
fi

extlinuximg="tmp/ts-$distro-installer.iso"

syslinuxdir="/usr/lib/syslinux/modules/bios"
for x in "/usr/lib/ISOLINUX/isolinux.bin" "tmp/initrd.xz" "tmp/debian-files/linux" "$syslinuxdir/vesamenu.c32" "$syslinuxdir/libcom32.c32" "$syslinuxdir/libutil.c32" "$syslinuxdir/ldlinux.c32"
do
  cp "$x" tmp/img/
done

cfg="tmp/img/isolinux.cfg"
echo "ui vesamenu.c32" 				 > "$cfg"
echo "TIMEOUT 20"				 >> "$cfg"
echo "label debian-installer"			 >> "$cfg"
echo "      menu label Debian $distro Installer" >> "$cfg"
echo "      menu default"			 >> "$cfg"
echo "      kernel /linux"			 >> "$cfg"
echo "      initrd /initrd.xz"			 >> "$cfg"
echo "Modify message"				 >> "$cfg"

mkisofs -o "tmp/ts-$distro-installer.iso" \
   -b isolinux.bin -c boot.cat \
   -no-emul-boot -boot-load-size 4 -boot-info-table \
   tmp/img

isohybrid "tmp/iso/ts-$distro-installer.iso"
