#! /usr/bin/env python
"""\
Scan for serial ports.

Part of pySerial (http://pyserial.sf.net)
(C) 2002-2003 <cliechti@gmx.net>

The scan function of this module tries to open each port number
from 0 to 255 and it builds a list of those ports where this was
successful.
"""

# import user module
import uart_var

def set_detailed_file(str):
	uart_var.detailed_result_path = str

def set_statistical_path(str):
	uart_var.statistical_result_path = str

def set_cmd_path(str):
	uart_var.cmd_file_path = str
	
def set_store_switch(x):
	uart_var.store_switch = x

def get_store_switch():
	return uart_var.store_switch

def set_count(i,x):
	uart_var.Count[i] = x

def get_count(i):
	return uart_var.Count[i]
	
def count_inc(i):
	uart_var.Count[i] = uart_var.Count[i] + 1

def show(str,mode):
	switch = get_store_switch()
	print str
	if switch == 1:
		f = open(uart_var.detailed_result_path,mode)
		print >> f, str
		f.close()

def store():
	f = open(uart_var.statistical_result_path,'w')
	#print uart_var.Count
	f.write('[TEST] send cmd count          = ' + hex(get_count(0)) + '\n')
	f.write('[TEST] test instructions count = ' + hex(get_count(1)) + '\n')
	f.write('[TEST] ok  instructions count  = ' + hex(get_count(2)) + '\n')
	f.write('[TEST] err instructions count  = ' + hex(get_count(3)) + '\n')
	f.close()
	
