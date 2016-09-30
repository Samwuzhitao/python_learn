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
import uart_var
import uart_message

def set_status(x):
	uart_var.status = x
#	print "set_status:",status

def get_status():
	return uart_var.status 

def set_cnt(x):
	uart_var.cnt = x
#	print "set_cnt:",cnt

def get_cnt():
	return uart_var.cnt 

def cnt_dec():
	uart_var.cnt = uart_var.cnt - 1
#	print "set_cnt:",uart_cnt

def xor_cal(x):
	uart_var.xor = uart_var.xor ^ ord(x)
	#print "xor_cal ouput data :",hex(uart_xor)

def set_xor(x):
	uart_var.xor = x

def get_xor():
	return uart_var.xor

def str_add(char):
	uart_var.str = uart_var.str + ' ' + char

def str_clear():
	uart_var.str = ""
	
def show(str):
	show_str = "Message->HEADER = "+str[1:3]
	uart_message.show(show_str,'a') 
	show_str = "Message->TYPE   = "+str[4:6]
	uart_message.show(show_str,'a')
	sign_str = str[7:18]
	show_str = "Message->SIGN   = "+sign_str
	uart_message.show(show_str,'a')
	len_str = str[19:21]
	show_str = "Message->LEN    = "+len_str
	uart_message.show(show_str,'a')
	len_int = string.atoi(len_str, 16)
	#print len_int
	data = str[22:22+len_int*3]
	show_str = "Message->DATA   = "+data
	uart_message.show(show_str,'a')
	xor = str[22+len_int*3:22+len_int*3+2]
	show_str = "Message->XOR    = "+xor
	uart_message.show(show_str,'a')
	end = str[22+(len_int+1)*3:22+(len_int+1)*3+2]
	show_str = "Message->END    = "+end+"\n"
	uart_message.show(show_str,'a')

def clear_pbuf(x):
	if x == 0:
		show(uart_var.str)
		str_clear()
	else:
		str_clear()

def revice_status_machine(x):
	char = "%02x" % ord(x)
	#print char
	uart_current_status = get_status()
	
	# revice header
	if uart_current_status == 0:
		if char == "5c":
			str_add(char)
			set_status(1)
		return
		
	# revice cmd type
	if uart_current_status == 1:
		str_add(char)
		xor_cal(x)
		set_status(2)
		set_cnt(4)
		return
	
	# rvice sign id
	if uart_current_status == 2:
		str_add(char)
		xor_cal(x)
		cnt_dec()
		uart_current_cnt = get_cnt()
		if uart_current_cnt == 0:
			set_status(3)
		return
	
	# revice message data len
	if uart_current_status == 3:
		str_add(char)
		xor_cal(x)
		if ord(x) == 0:
			set_status(5)
			return
		set_status(4)
		set_cnt(ord(x))
		#print "message len = ",ord(x)
		return
		
	# revoce data
	if uart_current_status == 4:
		str_add(char)
		xor_cal(x)
		cnt_dec() 
		uart_current_cnt = get_cnt()
		if uart_current_cnt == 0:
			set_status(5)
		return
	
	# revoce xor
	if uart_current_status == 5:
		uart_cal_oxr = get_xor()
		uart_cal_oxr = "%02x" % uart_cal_oxr
		#print "uart_revice_oxr =",char
		#print "xor_cal(x) =",uart_cal_oxr
		uart_oxr_cmp = cmp(uart_cal_oxr,char)
		#print uart_oxr_cmp
		uart_message.count_inc(1)
		if uart_oxr_cmp == 0:
			str_add(char)
			set_status(6)
			set_xor(0)
			uart_message.count_inc(2)
			return
		else:
			set_status(0)
			set_xor(0)
			# uart xor data err
			clear_pbuf(1)
			uart_message.count_inc(3)
			return

	# revice data end
	if uart_current_status == 6:
		if char == "ca":
			set_status(100)
			str_add(char)
			# uart xor data ok
			clear_pbuf(0)
			return

	
	