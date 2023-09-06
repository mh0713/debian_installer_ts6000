#!/usr/bin/python3

import time
import math
import serial
import sys

retry_count = 3

CMD_MODE_READ = 0x80

# Commands (not all commands supported by all versions)
bz_on = 0x30
lcd_set_linkspeed = 0x31
lcd_set_dispitem = 0x32
fan_set_speed = 0x33
system_get_mode = 0x34
system_set_watchdog = 0x35
int_get_switch_status = 0x36
fan_get_speed = 0x38
lcd_get_dispplane = 0x39
lcd_set_bright = 0x3a
usb_set_power = 0x3e
lcd_set_dispitem_ex = 0x40
power_state = 0x46
led_set_cpu_mcon = 0x50
bz_set_freq = 0x53
fan_get_speed_ex = 0x57
sata_led_set_on_off = 0x58
sata_led_set_blink = 0x59
lcd_set_disk_capacity = 0x60
lcd_set_date = 0x70
lcd_set_hostname = 0x80
lcd_set_ipaddress = 0x81
lcd_set_raidmode = 0x82
mcon_get_version = 0x83
mcon_get_taskdump = 0x84
boot_device_error = 0x93
lcd_set_raidmode32 = 0x94
lcd_set_buffer0 = 0xa0
lcd_set_buffer1 = 0xa1
lcd_set_buffer2 = 0xa2
lcd_set_buffer3 = 0xa3
lcd_set_buffer4 = 0xa4
lcd_set_buffer5 = 0xa5
lcd_set_buffer6 = 0xa6
lcd_set_buffer7 = 0xa7
lcd_init = 0x01
boot_start = 0x02
boot_end = 0x03
boot_dramdt_ng = 0x04
boot_dramad_ng = 0x05
power_off = 0x06
boot_flash_ok = 0x07
boot_dram_ok = 0x08
lcd_disp_animation = 0x09
boot_error_del = 0x0b
shutdown_wait = 0x0c
shutdown_cancel = 0x0d
reboot = 0x0e
serialmode_console = 0x0f
serialmode_ups = 0x10
ups_linefail_off = 0x11
ups_linefail_on = 0x12
ups_vender_apc = 0x13  # their spelling, not mine
ups_vender_omron = 0x14
lcd_disp_temp_on = 0x15
lcd_disp_temp_off = 0x16
lcd_changemode_button = 0x17
lcd_changemode_auto = 0x18
ups_shutdown_off = 0x19
ups_shutdown_on = 0x1a
lcd_disp_fanspeed_on = 0x1b
lcd_disp_fanspeed_off = 0x1c
bz_disp_on = 0x1d
bz_disp_off = 0x1e
lcd_disp_linkspeed = 0x20
lcd_disp_hostname = 0x21
lcd_disp_diskcap = 0x22
lcd_disp_raidmode = 0x23
lcd_disp_date = 0x24
lcd_disp_buffer0 = 0x25
lcd_disp_buffer1 = 0x26
lcd_disp_buffer2 = 0x27
shutdown_ups_recover = 0x28
wol_ready_on = 0x29
wol_ready_off = 0x2a
lcd_disp_buffer3 = 0x2b
lcd_disp_buffer4 = 0x2c
lcd_disp_buffer5 = 0x2d
lcd_disp_buffer6 = 0x2e
lcd_disp_buffer7 = 0x2f

BZ_STOP = 0x00
BZ_MACHINE = 0x01
BZ_BUTTON = 0x02
BZ_CONTINUE = 0x03
BZ_SWITCH1 = 0x04
BZ_SWITCH2 = 0x10
BZ_MUSIC1 = 0x30
BZ_MUSIC2 = 0x20

LED_ON = 1
LED_OFF = 0
LED_BLINK = 2

CMD_LED_CPU = 0x50
CMD_LED_ONOFF = 0x51
CMD_LED_BLINK = 0x52

POWER_LED = [0x09, 0x00]
INFO_LED = [0x02, 0x00]
ERROR_LED = [0x04, 0x00]
LAN1_LED = [0x20, 0x00]
LAN2_LED = [0x40, 0x00]
FUNC1_LED = [0x10, 0x00]
FUNC2_LED = [0x80, 0x00]
DISP_LED = [0x00, 0x80]

SATA_LED_ONOFF = 0x58
SATA_LED_BLINK = 0x59

SATA_ALL_LED = [0xFF, 0xFF]
SATA_ALL_RED = [0xFF, 0x00]
SATA1_RED = [0x01, 0x00]
SATA2_RED = [0x02, 0x00]
SATA3_RED = [0x04, 0x00]
SATA4_RED = [0x08, 0x00]
SATA5_RED = [0x10, 0x00]
SATA6_RED = [0x20, 0x00]
SATA7_RED = [0x40, 0x00]
SATA8_RED = [0x80, 0x00]

SATA_ALL_GREEN = [0x00, 0xFF]
SATA1_GREEN = [0x00, 0x01]
SATA2_GREEN = [0x00, 0x02]
SATA3_GREEN = [0x00, 0x04]
SATA4_GREEN = [0x00, 0x08]
SATA5_GREEN = [0x00, 0x10]
SATA6_GREEN = [0x00, 0x20]
SATA7_GREEN = [0x00, 0x40]
SATA8_GREEN = [0x00, 0x80]

LCD_BRIGHT_FULL = 0xFF
LCD_BRIGHT_LOW = 0x77
LCD_BRIGHT_MED = 0xCC
LCD_BRIGHT_OFF = 0x00

LCD_COLOR_RED = [0x00, 0x01]
LCD_COLOR_GREEN = [0x00, 0x02]
LCD_COLOR_ORANGE = [0x00, 0x03]
LCD_COLOR_BLUE = [0x00, 0x04]
LCD_COLOR_PURPLE = [0x00, 0x05]
LCD_COLOR_AQUA = [0x00, 0x06]
LCD_COLOR_MAGENTA = [0x00, 0x07]

GRAPH_0p = 0x00
GRAPH_25p = 0x04
GRAPH_50p = 0x08
GRAPH_75p = 0x0C
GRAPH_100p = 0x0F
GRAPH_ARROW = 0x10

LINK_NOLINK = 0x00
LINK_10M_HALF = 0x01
LINK_10M_FULL = 0x02
LINK_100M_HALF = 0x03
LINK_100M_FULL = 0x04
LINK_1000M = 0x05


class micon_api_v3:
    port = serial.Serial()
    debug = 0

    def __init__(self, serial_port="/dev/ttyS0", enable_debug=0):
        self.debug = enable_debug
        self.port = serial.Serial(serial_port, 57600, serial.EIGHTBITS, serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE, timeout=0.25)

    def send_miconv3(self, message):
        output = bytearray()
        output.extend(map(ord, message + "\r"))
        self.port.write(output)
        time.sleep(0.02)
        return self.recv_miconv3()

    def recv_miconv3(self):
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
