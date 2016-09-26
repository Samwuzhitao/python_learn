#! /usr/bin/env python
"""\
Scan for serial ports.

Part of pySerial (http://pyserial.sf.net)
(C) 2002-2003 <cliechti@gmx.net>

The scan function of this module tries to open each port number
from 0 to 255 and it builds a list of those ports where this was
successful.
"""

import serial
import array
import os
import signal
import time
import string
from time import sleep

flag_stop = False

cmd_DeviceInfo = "5C2C00000000002CCA"
cmd_DeviceInfo = cmd_DeviceInfo.decode("hex")

cmd_Systick = "5C2E00000000002ECA"
cmd_Systick = cmd_Systick.decode("hex")


def scan():
    """scan for available ports. return a list of tuples (num, name)"""
    available = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            available.append( (i, s.portstr))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return available

def discovery_uart():
    print "Found ports:"
    for n,s in scan():
        print "(%d) %s" % (n,s)

		
def uart_change_status(x):
	global status
	status = x
#	print "uart_change_status:",status

def uart_change_uart_cnt(x):
	global uart_cnt
	uart_cnt = x
#	print "uart_change_uart_cnt:",uart_cnt

def uart_change_uart_cnt_dec():
	global uart_cnt
	uart_cnt = uart_cnt - 1
#	print "uart_change_uart_cnt:",uart_cnt

def uart_add_char_to_pbuf(char):
	global printf_str
	printf_str = printf_str + ' '+char

def str_2_hex_to_int(str):
	sStr1 = str[0:2]
	num = string.atoi(sStr1, 16)
	print num

def str_1_hex_to_2_hex(str):
	sStr1 = str
	
	sStr2 = sStr1.split(' 0')
	delimiter = ' 00'
	sStr2 = delimiter.join(sStr2)
	return sStr2


def uart_show_message(str):
	sStr1 = str
	
	sStr2 = sStr1.split(' 0')
	delimiter = ' 00'
	sStr2 = delimiter.join(sStr2)
	
	print sStr2
	
	print "Message->header =",sStr2[1:3]
	print "Message->Type   =",sStr2[4:6]
	
	sign_str = sStr2[7:18]
	print "Message->SIGN   =",sign_str
	
	len_str = sStr2[19:21]
	print "Message->LEN    =",len_str
	len_int = string.atoi(len_str, 16)
	print len_int
	
	data = sStr2[22:22+len_int*3]
	print "Message->DATA    = ",data
	
	xor = sStr2[222+len_int*3+1:22+len_int*3+3]
	print "Message->OXR    = ",xor
	
	
def uart_clear_pbuf():
	global printf_str
	print printf_str
	uart_show_message(printf_str)
	printf_str = ""
	
def uart_change_test_cnt(data):
	global test_cnt
	test_cnt = test_cnt + data
	print "uart_change_test_cnt:",test_cnt

	
def uart_decode_machine(x):
	global status
	global uart_cnt
	
	char = hex(ord(x))[2:]

	# revice header
	if status == 0:
		if char == "5c":
			uart_add_char_to_pbuf(char)
			uart_change_status(1)
		return
		
	# revice cmd type
	if status == 1:
		uart_add_char_to_pbuf(char)
		uart_change_status(2)
		uart_change_uart_cnt(4)
		return
	
	# rvice sign id
	if status == 2:
		uart_add_char_to_pbuf(char)
		uart_change_uart_cnt_dec() 
		if uart_cnt == 0:
			uart_change_status(3)
		return
	
	# revice message data len
	if status == 3:
		uart_add_char_to_pbuf(char)
		if ord(x) == 0:
			uart_change_status(5)
			return
		uart_change_status(4)
		uart_change_uart_cnt(ord(x))
		print "message len = ",ord(x)
		return
		
	# revoce data
	if status == 4:
		uart_add_char_to_pbuf(char)
		uart_change_uart_cnt_dec() 
		if uart_cnt == 0:
			uart_change_status(5)
		return
	
	# revice data end
	if status == 5:	
		if char == "ca":
			uart_change_status(100)
			uart_add_char_to_pbuf(char)
			uart_clear_pbuf()
			return

	
if __name__=='__main__':
	status = 0
	printf_str = ""
	uart_cnt = 0
	test_cnt = 0
	
	discovery_uart();
#	selport = input('please select port:')
	selport = 5 
	print "the port you select is :",selport
#	ser = serial.Serial( selport, 115200)
	ser = serial.Serial( selport, 115200, timeout = 1)
	print "Open", ser.portstr
	print "serial.isOpen() =",ser.isOpen()
			
	startTime = time.time()
	
	print "Uart Message process :"
	while True: 
		# send cmd meaasge
		ser.write(cmd_DeviceInfo)
		
		# decode return message 
		while True:
			read_char = ser.read(1)
			uart_decode_machine(read_char)
			if status == 100:
				uart_change_status(0)
				break
				
		# Statistical time 
		uart_change_test_cnt(1)		
		endTime = time.time()
		print "use time: "+str(endTime-startTime)
		
		# delay 500 ms
		sleep(0.5)

#	if n == 5:
#	
#		while True:    
#			data =recv(ser)    
#			ser.write(data)
 
	#print "please selsect serial port:"
	
	
	