#!/usr/bin/python3

import libmicon
import platform
import socket


###make miconv2 and v3 start up tasks functions.

def get_title():
	return "Buffalo Cache"

def get_hostname():
	return socket.gethostname()

def startupV2(port):
	micon = libmicon.micon_api(port)

	micon_version = micon.send_read_cmd(0x83)
	micon_version=micon_version.decode('utf-8')

	##disable boot watchdog
	micon.send_write_cmd(0,0x03)

	title = get_title().center(16)
	version= get_hostname().center(16)

	### need to understand variations of this
	##turn of red drive leds
	micon.cmd_set_led(libmicon.LED_OFF,[0x00,0x0F])

	micon.set_lcd_buffer(0x90,title,version)
	micon.cmd_force_lcd_disp(libmicon.lcd_disp_buffer0)
	micon.send_write_cmd(1,libmicon.lcd_set_dispitem,0x20)
	micon.set_lcd_brightness(libmicon.LCD_BRIGHT_FULL)

	if (micon_version.find("HTGL") == -1):
		micon.set_lcd_color(libmicon.LCD_COLOR_GREEN)

	micon.cmd_set_led(libmicon.LED_ON,libmicon.POWER_LED)

	micon.port.close()

def startupV3(port):
	micon = libmicon.micon_api_v3(port)

	##disable watchdog
	micon.send_miconv3("BOOT_END")

	title = get_title().center(16,u"\u00A0")
	version = get_hostname().center(16,u"\u00A0")

	print(micon.set_lcd(0,title))
	print(micon.set_lcd(1,version))

	##solid power LED
	micon.set_led(0,"on")
	micon.port.close()

# check for some sort of config file to avoid messing with ports each time?

##try reading micon version from each port to determine the right one
for port in ["/dev/ttyS1","/dev/ttyS3"]:
	try:
		micon = libmicon.micon_api(port)
	except:
		continue
	micon_version = micon.send_read_cmd(0x83)
	if micon_version:
		micon.port.close()
		startupV2(port)
		quit()
	micon.port.close()


for port in ["/dev/ttyUSB0","/dev/ttyS1","/dev/ttyS0"]:
	try:
		micon = libmicon.micon_api_v3(port)
	except:
		continue
	micon_version = micon.send_miconv3("VER_GET")
	if micon_version:
		micon.port.close()
		startupV3(port)
		quit()
	micon.port.close()

quit()
