#!/usr/bin/python3

import libmicon
import time
import sys


def shutdownV3(port):
	test = libmicon.micon_api_v3(port)
	if sys.argv[1] in ["halt","poweroff"]:
		test.send_miconv3("SHUTDOWN")
	else:
		test.send_miconv3("REBOOT")
	test.port.close()


for port in ["/dev/ttyUSB0","/dev/ttyS1","/dev/ttyS0"]:
	try:
		test = libmicon.micon_api_v3(port)
	except:
		continue
	micon_version = test.send_miconv3("VER_GET")
	if micon_version:
		test.port.close()
		shutdownV3(port)
		quit()
	test.port.close()

quit()
