#!/bin/bash

set -o errexit

# 変数定義
cur_dir=$(cd $(dirname $0); pwd)
src_dir="${cur_dir}"/src
orig_iso="${cur_dir}"/base_iso/debian-12.1.0-amd64-netinst.iso
new_files="${cur_dir}"/tmp/
new_iso="${new_files}"/bookworm-installer-ts6000.iso
mbr_template=isohdpfx.bin

cd "${cur_dir}"

# 作業ディレクトリのクリーンアップ＆作成
sudo rm -rf ${new_files}
mkdir -p ${new_files}


# 必要なツールのインストール
sudo apt update
sudo apt -y install cpio syslinux isolinux xorriso mkisofs syslinux-utils pigz

#Extracting the Initrd from an ISO Image
xorriso -osirrox on -indev "$orig_iso" -extract / "$new_files"

#Adding a Preseed File to the Initrd
chmod +w -R "${new_files}"/install.amd/
gunzip "${new_files}"/install.amd/initrd.gz

pushd "${src_dir}"
echo "preseed.cfg" | cpio -H newc -o -A -F "${new_files}"/install.amd/initrd
echo "bin/early_cmds.sh" | cpio -H newc -o -A -F "${new_files}"/install.amd/initrd
echo "bin/micro-evtd" | cpio -H newc -o -A -F "${new_files}"/install.amd/initrd
popd
pigz "${new_files}"/install.amd/initrd
chmod -w -R "${new_files}"/install.amd/

# cfg="${new_files}/isolinux/isolinux.cfg"
# chmod +w ${cfg}
# echo "ui vesamenu.c32" 				 > "$cfg"
# echo "TIMEOUT 10"				 >> "$cfg"
# echo "label debian-installer"			 >> "$cfg"
# echo "      menu label Debian $distro Installer" >> "$cfg"
# echo "      menu default"			 >> "$cfg"
# echo "      kernel /linux"			 >> "$cfg"
# echo "      initrd /initrd.xz"			 >> "$cfg"
# echo "Modify message"				 >> "$cfg"
# chmod -w ${cfg}

sudo cp "${src_dir}"/grub.cfg "${new_files}"/boot/grub/

sudo mkdir "${new_files}"/src/
sudo cp -r "${src_dir}"/* "${new_files}"/src/

#Regenerating md5sum.txt
cd "${new_files}"
chmod +w md5sum.txt

find -follow -type f ! -name md5sum.txt -print0 | xargs -0 md5sum > md5sum.txt
chmod -w md5sum.txt
cd "${cur_dir}"

dd if="${orig_iso}" bs=1 count=432 of="${mbr_template}"

#ブータブルISOの作成
sudo xorriso -as mkisofs \
   -r -V 'TS6000 bookworm installer n' \
   -o "${new_iso}" \
   -J -J -joliet-long -cache-inodes \
   -isohybrid-mbr "${mbr_template}" \
   -b isolinux/isolinux.bin \
   -c isolinux/boot.cat \
   -boot-load-size 4 -boot-info-table -no-emul-boot \
   -eltorito-alt-boot \
   -e boot/grub/efi.img \
   -no-emul-boot -isohybrid-gpt-basdat -isohybrid-apm-hfsplus \
   "${new_files}"
