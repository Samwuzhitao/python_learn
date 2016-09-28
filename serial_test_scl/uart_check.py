#! /usr/bin/env python
"""\
Scan for serial ports.

Part of pySerial (http://pyserial.sf.net)
(C) 2002-2003 <cliechti@gmx.net>

The scan function of this module tries to open each port number
from 0 to 255 and it builds a list of those ports where this was
successful.
"""

# global variable
uart_revice_cmd_ok_num = 0
uart_revice_cmd_err_num = 0

def uart_change_uart_revice_cmd_ok_num(data):
	global uart_revice_cmd_ok_num
	uart_revice_cmd_ok_num = uart_revice_cmd_ok_num + data
	print "uart_change_uart_revice_cmd_ok_num:",uart_revice_cmd_ok_num

def uart_change_uart_revice_cmd_err_num(data):
	global uart_revice_cmd_err_num
	uart_revice_cmd_err_num = uart_revice_cmd_err_num + data
	print "uart_change_uart_revice_cmd_err_num:",uart_revice_cmd_err_num