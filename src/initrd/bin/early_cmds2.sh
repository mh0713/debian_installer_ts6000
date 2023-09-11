#!/bin/sh -x

set -o errexit

[ "x$(cat /sys/devices/virtual/dmi/id/product_name)" != "xTeraStation" ] && exit 0

## send MiconV3 get version command
## probably harmless on miconv2 devs but may as well avoid.
/bin/micro-evtd -p /dev/ttyS0 -s3 "VER_GET"

#if that succeeded setup LCD/LEDS via MiconV3
if [ $? -eq 0 ]; then
  IP=$(ip a | grep "inet " | grep -v "scope host" | head -n 1 | cut -d " " -f 6)
  ## set LCD message
  /bin/micro-evtd -p /dev/ttyS0 -s3 "LCD_PUTS 1 ${IP%/*}"
fi

exit 0
