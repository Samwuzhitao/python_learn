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
import string

# import user module
import uart_check

# global variable
status = 0
uart_cnt = 0
uart_xor = 0
printf_str = ""

def uart_change_status(x):
	global status
	status = x
#	print "uart_change_status:",status

def uart_get_status():
	global status
	return status 

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

def uart_clear_pbuf(x):
	global printf_str
	#print printf_str
	if x == 0:
		uart_show_message(printf_str)
		printf_str = ""
		uart_check.uart_change_uart_revice_cmd_ok_num(1)
	else:
		printf_str = ""
		uart_check.uart_change_uart_revice_cmd_err_num(1)
		
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

	
	