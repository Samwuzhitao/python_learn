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
import linecache 
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

def uart_xor_cal(x):
	global uart_xor
	#print "uart_xor_cal input data :",hex(ord(x))
	uart_xor = uart_xor ^ ord(x)
	#print "uart_xor_cal ouput data :",hex(uart_xor)

def uart_change_xor(x):
	global uart_xor
	uart_xor = x

def uart_get_xor():
	global uart_xor
	return uart_xor

	
def uart_show_message(str):
	print "Message->HEADER =",str[1:3]
	print "Message->TYPE   =",str[4:6]
	
	sign_str = str[7:18]
	print "Message->SIGN   =",sign_str
	
	len_str = str[19:21]
	print "Message->LEN    =",len_str
	len_int = string.atoi(len_str, 16)
	#print len_int
	
	data = str[22:22+len_int*3]
	print "Message->DATA   =",data

	Message_xor = str[22+len_int*3:22+len_int*3+2]
	print "Message->XOR    =",Message_xor

	Message_end = str[22+(len_int+1)*3:22+(len_int+1)*3+2]
	print "Message->END    =",Message_end
	
def uart_change_test_cnt_ok(data):
	global test_cnt_ok
	test_cnt_ok = test_cnt_ok + data
	print "uart_change_test_cnt_ok:",test_cnt_ok

def uart_change_test_cnt_err(data):
	global test_cnt_err
	test_cnt_err = test_cnt_err + data
	print "uart_change_test_cnt_err:",test_cnt_err
	
def uart_clear_pbuf(x):
	global printf_str
	#print printf_str
	if x == 0:
		uart_show_message(printf_str)
		printf_str = ""
		uart_change_test_cnt_ok(1)
	else:
		printf_str = ""
		uart_change_test_cnt_err(1)
	
def uart_decode_machine(x):
	global status
	global uart_cnt
	global uart_xor
	
	char = "%02x" % ord(x)
	#print char

	# revice header
	if status == 0:
		if char == "5c":
			uart_add_char_to_pbuf(char)
			uart_change_status(1)
		return
		
	# revice cmd type
	if status == 1:
		uart_add_char_to_pbuf(char)
		uart_xor_cal(x)
		uart_change_status(2)
		uart_change_uart_cnt(4)
		return
	
	# rvice sign id
	if status == 2:
		uart_add_char_to_pbuf(char)
		uart_xor_cal(x)
		uart_change_uart_cnt_dec()
		if uart_cnt == 0:
			uart_change_status(3)
		return
	
	# revice message data len
	if status == 3:
		uart_add_char_to_pbuf(char)
		uart_xor_cal(x)
		if ord(x) == 0:
			uart_change_status(5)
			return
		uart_change_status(4)
		uart_change_uart_cnt(ord(x))
		#print "message len = ",ord(x)
		return
		
	# revoce data
	if status == 4:
		uart_add_char_to_pbuf(char)
		uart_xor_cal(x)
		uart_change_uart_cnt_dec() 
		if uart_cnt == 0:
			uart_change_status(5)
		return
	
	# revoce xor
	if status == 5:
		uart_cal_oxr = uart_get_xor()
		uart_cal_oxr = "%02x" % uart_cal_oxr
		#print "uart_revice_oxr =",char
		#print "uart_xor_cal(x) =",uart_cal_oxr
		uart_oxr_cmp = cmp(uart_cal_oxr,char)
		#print uart_oxr_cmp
		if uart_oxr_cmp == 0:
			uart_add_char_to_pbuf(char)
			uart_change_status(6)
			uart_change_xor(0)
			return
		else:
			uart_change_status(0)
			uart_change_xor(0)
			# uart xor data err
			uart_clear_pbuf(1)
			return

	# revice data end
	if status == 6:
		if char == "ca":
			uart_change_status(100)
			uart_add_char_to_pbuf(char)
			# uart xor data ok
			uart_clear_pbuf(0)
			return


			
def uart_get_cmd_message():
	global 	uart_test_cmd_max
	global uart_test_cmd_index
	
	f = open(uart_test_file_name,'r')
	uart_read_cmd = linecache.getline(uart_test_file_name,uart_test_cmd_index+1)
	print "uart send cmd : "+uart_read_cmd
	uart_read_cmd = linecache.getline(uart_test_file_name,uart_test_cmd_index+2)
	#print "linecache.getline = "+uart_read_cmd
	linecache.clearcache()
	f.close()
	
	uart_test_cmd_index = uart_test_cmd_index + 2 
	if uart_test_cmd_index == uart_test_cmd_max:
		uart_test_cmd_index = 0

	uart_read_cmd=uart_read_cmd.strip('\n')

	return uart_read_cmd

if __name__=='__main__':
	status = 0
	printf_str = ""
	uart_cnt = 0
	test_cnt_ok = 0
	test_cnt_err = 0
	uart_xor = 0
	uart_test_cmd_max = 0
	uart_test_cmd_index = 0
	uart_test_cmd_num = 0
	uart_test_file = ""
	
	# open uart port
	discovery_uart();
	selport = input('please select port:')
#	selport = 5 
	print "the port you select is :",selport
	ser = serial.Serial( selport, 115200, timeout = 120)
#	ser = serial.Serial( selport, 115200, timeout = 120)
	print "Open", ser.portstr
	print "serial.isOpen() =",ser.isOpen()

	# open read test file name
	f = open('clicker_test_cmd_file_select.txt','r')
	uart_test_file_name = linecache.getline('clicker_test_cmd_file_select.txt',1)
	uart_test_file_name=uart_test_file_name.strip('\n')
	print "uart test file name : "+uart_test_file_name
	f.close()
	
	# get the cmd num of the file 'clicker_test_cmd.txt'
	uart_test_cmd_max = len(open(uart_test_file_name,'rU').readlines()) 
	print "clicker_test_cmd len = ",uart_test_cmd_max/2

	startTime = time.time()

	print "Uart Message process :"
	while True: 
		# send cmd meaasge
		#ser.write(cmd_DeviceInfo)
		#ser.write(cmd_Systick)
		
		uart_cmd_data = uart_get_cmd_message()
		#print uart_cmd_data
		uart_cmd_data = uart_cmd_data.decode("hex")
		ser.write(uart_cmd_data)
		uart_test_cmd_num = uart_test_cmd_num + 1
		# decode return message 
		
		while True:
			read_char = ser.read(1)
			uart_decode_machine(read_char)
			if status == 100:
				uart_change_status(0)
				break
				
		# Statistical time 
		endTime = time.time()
		f = open('clicker_test_result.txt','w')
		f.write('uart test count     = '+hex(uart_test_cmd_num)+'\r\n')
		f.write('uart test ok count  = '+hex(test_cnt_ok)+'\r\n')
		f.write('uart test err count = '+hex(test_cnt_err)+'\r\n')
		f.write('uart test time      = '+str(endTime-startTime)+'\r\n')
		f.close()
		#print "use time: "+str(endTime-startTime)
		
		# delay 500 ms
		#sleep(0.05)

#	if n == 5:
#	
#		while True:    
#			data =recv(ser)    
#			ser.write(data)
 
	#print "please selsect serial port:"
	
	
	