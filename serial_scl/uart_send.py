#! /usr/bin/env python
"""\
Scan for serial ports.

Part of pySerial (http://pyserial.sf.net)
(C) 2002-2003 <cliechti@gmx.net>

The scan function of this module tries to open each port number
from 0 to 255 and it builds a list of those ports where this was
successful.
"""
# import system module
import ConfigParser

# import user module
import uart_var
import uart_message

def set_test_max(x):
	uart_var.TEST_MAX = x
#	print "set_status:",status

def get_test_max():
	return uart_var.TEST_MAX

def set_test_index(x):
	uart_var.test_index = x
#	print "set_status:",status

def get_test_index():
	return uart_var.test_index

def test_index_inc():
	uart_var.test_index = uart_var.test_index + 1

def set_max(x):
	uart_var.max = x
#	print "set_status:",status

def get_max():
	return uart_var.max
	
def set_index(x):
	uart_var.index = x
#	print "set_status:",status

def add_index(x):
	uart_var.index = uart_var.index + x
	
def get_index():
	return uart_var.index

def update_index():
	add_index(2)
	uart_message.count_inc(0)
	if uart_var.index == uart_var.max:
		set_index(0)
		test_index_inc()

def init_cmds(file_name):
	cmd_len = len(open(file_name,'rU').readlines()) 
	set_max(cmd_len)
	f = open(file_name,'rU')
	uart_var.cmds =f.readlines()
	#print uart_var.cmds
	f.close()
	print "clicker_test_cmd len = ",cmd_len/2

def get_cmd_des():
	i = get_index()
	return uart_var.cmds[i]
	
def get_cmd_data():
	i = get_index()
	update_index()
	return uart_var.cmds[i+1]


	
	