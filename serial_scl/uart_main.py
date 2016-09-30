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
import serial
import os
import time
import string
import linecache 
import threading
import ConfigParser
import sys
from time import sleep

# import user module
import uart_init  
import uart_decode
import uart_send
import uart_message

def uart_compress_cmd_process():
	global ser
	
	while True:
		read_char = ser.read(1)
		uart_decode.revice_status_machine(read_char)
		uart_current_status = uart_decode.get_status()
		#print "uart_current_status = ",uart_current_status
		if uart_current_status == 100:
			uart_decode.set_status(0)
			uart_message.store()


def uart_send_cmd_process():
	global ser

	while True:
		# step 1: get cmd description
		uart_cmd_des = uart_send.get_cmd_des()
		uart_cmd_des = uart_cmd_des.strip('\n')
		uart_message.show(uart_cmd_des,'a')
		
		# step 2: get cmd data
		uart_cmd_data = uart_send.get_cmd_data()
		uart_cmd_data = uart_cmd_data.strip('\n')
		uart_message.show(uart_cmd_data,'a')
		
		# step 3:send data
		uart_cmd_data = uart_cmd_data.decode("hex")
		ser.write(uart_cmd_data)
		sleep(string.atoi(send_delayms, 10)*1.0/1000)
		
		#step 4:check test times 
		if(uart_send.get_test_index() == uart_send.get_test_max()):
			sys.exit(0)

if __name__=='__main__':
	# open uart port
	uart_init.uart_scan();
	path = os.path.abspath("../")
	print 'Please Ensure you have config the serial port in:'
	print path + '\\configuration\\' + 'uart_config.txt'
	selport = raw_input("Press any key continue ...")
	
	# get uart configuration
	config = ConfigParser.ConfigParser()
	config.readfp(open(path + '\\configuration\\' + 'uart_config.txt', "rb"))
	selport                = config.get('setting', 'Port')
	baudrate               = config.get('setting', 'baudrate')
	timeout                = config.get('setting', 'timeout')
	send_delayms           = config.get('setting', 'send_delayms')
	uart_file_store_switch = config.get('setting', 'file_store_switch')
	uart_cmd_file_name    = config.get('cmd_file_setting', 'cmd_file_name')
	test_max               = config.get('cmd_file_setting', 'test_max')
	
	# update store switch status
	uart_message.set_store_switch(string.atoi(uart_file_store_switch, 10))
	
	# get current date
	ISOTIMEFORMAT = '%Y-%m-%d-%H-%M-%S'
	now = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )

	# show test file path
	path = path + '\\test_file\\'
	uart_cmd_file              = path + uart_cmd_file_name
	uart_test_temp_result_file = path + 'clicker_temp_result-' + now + '.txt'
	uart_test_result_file      = path + 'clicker_test_result-' + now +'.txt'
	
	uart_message.set_cmd_path(uart_cmd_file)
	uart_message.set_detailed_file(uart_test_temp_result_file)
	uart_message.set_statistical_path(uart_test_result_file)
	
	# open serial port
	ser = serial.Serial( string.atoi(selport, 10), string.atoi(baudrate, 10), timeout = string.atoi(timeout, 10))
	show_str = "Config Port :  "+selport
	uart_message.show(show_str,'w')
	show_str = "Open Port   :  "+ser.portstr
	uart_message.show(show_str,'a')
	show_str = "Baudrate    :  "+baudrate
	uart_message.show(show_str,'a')
	show_str = "TimeOut     :  "+timeout
	uart_message.show(show_str,'a')
	show_str = "Send delayms:  "+send_delayms
	uart_message.show(show_str,'a')
	show_str = "File Store Switch:  "+uart_file_store_switch
	uart_message.show(show_str,'a')

	show_str = "Test Start Time : " + now
	uart_message.show(show_str,'a')
	
	# init uart test file times
	show_str =  "uart test file test times : "+test_max
	uart_message.show(show_str,'a')
	test_max = string.atoi(test_max, 10)
	uart_send.set_test_max(test_max)
	
	show_str = "Test cmd file            : "+uart_cmd_file
	uart_message.show(show_str,'a')
	show_str = "Test detailed results    : "+uart_test_temp_result_file
	uart_message.show(show_str,'a')
	show_str = "Test statistical results : "+uart_test_result_file
	uart_message.show(show_str,'a')
	
	uart_send_cmd_switch = input('Open or Close cmd send function : ( 0 : [OFF] , 1 : [ON] ) ')

	if uart_send_cmd_switch == 1:
		uart_send.init_cmds(uart_cmd_file)

	#while True:
	#   if uart_send_cmd_switch == 1:
	#		uart_send_cmd_process()
	#	uart_compress_cmd_process()

	reader  = threading.Thread(target=uart_compress_cmd_process)
	print 'Process reader is going to start...'
	reader.start()
	

	if uart_send_cmd_switch == 1:
		writer  = threading.Thread(target=uart_send_cmd_process)
		print 'Process writer is going to start...'
		writer .start()
		
