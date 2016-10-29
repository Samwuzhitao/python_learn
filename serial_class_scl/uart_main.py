#! /usr/bin/env python
#coding:utf-8
"""\
uart_main for serial ports.

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
import uart_send
import uart_decode
import uart_message

def uart_compress_cmd_process():
	global ser
	global uartr
	global uartm
	global uarts

	while True:
		read_char = ser.read(1)
		uartr.revice_status_machine(read_char,uartm.message_show,uartm.count_inc)
		uart_current_status = uartr.get_status()
		#print "uart_current_status = ",uart_current_status
		if uart_current_status == 100:
			uartr.set_status(0)
			uartm.store()

def uart_send_cmd_process():
	global ser
	global uartr
	global uartm
	global uarts

	uarts.userflg = input('User or Auto cmd send : ( 0 : [user] , 1 : [auto] ) ')

	if uarts.userflg == 1:
		while True:
			# step 1: get cmd description
			uart_cmd_des = uarts.get_cmd_des()
			uart_cmd_des = uart_cmd_des.strip('\n')
			if uart_cmd_des[0:1] == "<":
				uartm.show(uart_cmd_des[4:],'a')
			else:
				uartm.show(uart_cmd_des,'a')

			# step 2: get cmd data
			uart_cmd_data = uarts.get_cmd_data(uartm.count_inc)
			# 剔除换行符
			uart_cmd_data = uart_cmd_data.strip('\n')
			uartm.show(" "+uart_cmd_data,'a')
			# 剔除多余空格
			uart_cmd_data = uart_cmd_data.replace(' ','')

			# step 3:send data
			uart_cmd_data = uart_cmd_data.decode("hex")
			ser.write(uart_cmd_data)

			if uart_cmd_des[0:1] == "<":
				#print "%d ms" % (string.atoi(uart_cmd_des[1:3], 10)*1000)
				sleep(string.atoi(uart_cmd_des[1:3], 10)*1000.0/1000)
			else:
				#print "%d ms" % (string.atoi(send_delayms, 10))
				sleep(string.atoi(send_delayms, 10)*1.0/1000)

			#step 4:check test times
			if(uarts.get_test_index() == uarts.get_test_max()):
				sys.exit(0)
	else:
		while True:
			uart_cmd_des = uarts.get_user_des()
			uart_cmd_des = uart_cmd_des.strip('\n')
			if uart_cmd_des[0:1] == "<":
				uartm.show(uart_cmd_des[4:],'a')
			else:
				uartm.show(uart_cmd_des,'a')

			uart_cmd_data = uarts.get_user_cmd()
			# 剔除换行符
			uart_cmd_data = uart_cmd_data.strip('\n')
			# 剔除多余空格
			uart_cmd_data = uart_cmd_data.replace(' ','')
			# step 3:send data
			uart_cmd_data = uart_cmd_data.decode("hex")
			ser.write(uart_cmd_data)

			sleep(string.atoi(uart_cmd_des[1:3], 10)*1000.0/1000)


if __name__=='__main__':
	#system init
	uarts = uart_send.UartS()
	uartr = uart_decode.UartR()
	uartm = uart_message.UartM()

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
	uart_cmd_file_name     = config.get('cmd_file_setting', 'cmd_file_name')
	test_max               = config.get('cmd_file_setting', 'test_max')

	# update store switch status
	uartm.set_store_switch(string.atoi(uart_file_store_switch, 10))

	# get current date
	ISOTIMEFORMAT = '%Y-%m-%d-%H-%M-%S'
	now = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )

	# show test file path
	path = path + '\\test_file\\'
	uart_cmd_file              = path + uart_cmd_file_name
	uart_test_temp_result_file = path + 'clicker_temp_result-' + now + '.txt'
	uart_test_result_file      = path + 'clicker_test_result-' + now +'.txt'

	uartm.set_cmd_path(uart_cmd_file)
	uartm.set_detailed_file(uart_test_temp_result_file)
	uartm.set_statistical_path(uart_test_result_file)

	# open serial port
	ser = serial.Serial( string.atoi(selport, 10), string.atoi(baudrate, 10), timeout = string.atoi(timeout, 10))
	show_str = "Config Port :  "+selport
	uartm.show(show_str,'w')
	show_str = "Open Port   :  "+ser.portstr
	uartm.show(show_str,'a')
	show_str = "Baudrate    :  "+baudrate
	uartm.show(show_str,'a')
	show_str = "TimeOut     :  "+timeout
	uartm.show(show_str,'a')
	show_str = "Send delayms:  "+send_delayms
	uartm.show(show_str,'a')
	show_str = "File Store Switch:  "+uart_file_store_switch
	uartm.show(show_str,'a')
	show_str = "Test Start Time  : " + now
	uartm.show(show_str,'a')

	# init uart test file times
	show_str =  "uart test file test times : "+test_max
	uartm.show(show_str,'a')
	test_max = string.atoi(test_max, 10)
	uarts.set_test_max(test_max)

	show_str = "Test cmd file            : "+uart_cmd_file
	uartm.show(show_str,'a')
	show_str = "Test detailed results    : "+uart_test_temp_result_file
	uartm.show(show_str,'a')
	show_str = "Test statistical results : "+uart_test_result_file
	uartm.show(show_str,'a')

	uart_send_cmd_switch = input('Open or Close cmd send function : ( 0 : [OFF] , 1 : [ON] ) ')

	if uart_send_cmd_switch == 1:
		uarts.init_cmds(uart_cmd_file)

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

