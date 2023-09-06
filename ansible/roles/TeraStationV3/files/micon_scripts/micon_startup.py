#!/usr/bin/python3

import libmicon
import platform
import socket


###make miconv2 and v3 start up tasks functions.

def get_title():
	return "Buffalo Cache"

def get_hostname():
	return socket.gethostname()

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
