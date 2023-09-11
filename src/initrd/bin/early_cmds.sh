#!/bin/sh -x

set -o errexit

[ "x$(cat /sys/devices/virtual/dmi/id/product_name)" != "xTeraStation" ] && exit 0

## send MiconV3 get version command
## probably harmless on miconv2 devs but may as well avoid.
/bin/micro-evtd -p /dev/ttyS0 -s3 "VER_GET"

#if that succeeded setup LCD/LEDS via MiconV3
if [ $? -eq 0 ]; then
  ## Set Power LED to on
  /bin/micro-evtd -p /dev/ttyS0 -s3 "LED_ON 0"

  ## set LCD message
  /bin/micro-evtd -p /dev/ttyS0 -s3 "LCD_PUTS 0 Terastation x86","LCD_PUTS 1 Debian Installer"

fi

exit 0
