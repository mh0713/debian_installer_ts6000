#!/bin/bash

boot_parts=$(btrfs device usage / | grep /dev/ | cut -d ',' -f 1)

for part in ${boot_parts}; do
   dev=$(lsblk -dprn -o PKNAME ${part})
   grub-install ${dev} 
done