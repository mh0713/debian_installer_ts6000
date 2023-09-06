#!/usr/bin/env python3

import argparse
import time
import math
import serial
import sys

retry_count = 3

class micon_api_v3:
    port = serial.Serial()
    debug = 0

    def __init__(self, serial_port="/dev/ttyS0", enable_debug=0):
        self.debug = enable_debug
        self.port = serial.Serial(serial_port, 57600, serial.EIGHTBITS, serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE, timeout=0.25)

    def send(self, message):
        output = bytearray()
        output.extend(map(ord, message + "\r"))
        self.port.write(output)
        time.sleep(0.02)
        return self.recv()

    def recv(self):
        return self.port.readline()

    def set_led(self, led, state, blinkrate=500):
        cmd = "LED_" + state.upper() + " " + str(led) + " " + str(blinkrate)
        return self.send_miconv3(cmd)

    def set_lcd(self, linenum, msg):
        cmd = "LCD_PUTS " + str(linenum) + " " + msg
        return self.send_miconv3(cmd)

    def sound(self, freq, duration):
        cmd = "SOUND " + str(freq) + " " + str(duration)
        return self.send_miconv3(cmd)

    def eeprom_read(self, bytenum):
        cmd = "EEPROM_READ " + str(bytenum) + " " + "1"
        return self.send_miconv3(cmd)

    def eeprom_print(self, bytecount):
        width = 16
        lines = math.ceil(bytecount / width)
        for y in range(lines):
            hexline = " "
            strline = ""
            byte = (y * width)
            prefix = "0x" + hex(byte).split("x")[1].rjust(4, "0")
            print(prefix + " ", end='')
            for x in range(width):
                byte = (y * width) + x
                result = self.eeprom_read(byte)
                resultint = int(result)
                resultbyte = resultint.to_bytes(1, 'big')
                resultchar = (str(resultbyte, 'utf-8'))
                if not (resultchar.isprintable()):
                    resultchar = "."
                strline = strline + resultchar
                resulthex = resultbyte.hex()
                hexline = hexline + " " + resulthex
            print(hexline + " ", "|" + strline + "|")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('msg')
    args = parser.parse_args()

    m = micon_api_v3()
    r = m.send(args.msg)

    if r.decode().startswith('DONE'):
        sys.exit(0)
    elif args.msg == "VER_GET" and len(r.decode())>2:
        sys.exit(0)
    else:
        sys.exit(255)



if __name__ == '__main__':
    main()