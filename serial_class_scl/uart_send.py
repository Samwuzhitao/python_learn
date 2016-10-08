#! /usr/bin/env python
"""\
Scan for serial ports.

Part of pySerial (http://pyserial.sf.net)
(C) 2002-2003 <cliechti@gmx.net>

The scan function of this module tries to open each port number
from 0 to 255 and it builds a list of those ports where this was
successful.
"""
import ConfigParser
import os
import time

class UartS():
	def __init__(self):
		self.TEST_MAX   = 0
		self.test_index = 0
		self.index      = 0
		self.cmds       = []
		#print "UartS Class init Ok!"

	def set_test_max(self,x):
		self.TEST_MAX = x
	#	print "set_status:",status

	def get_test_max(self):
		return self.TEST_MAX

	def set_test_index(self,x):
		self.test_index = x
	#	print "set_status:",status

	def get_test_index(self):
		return self.test_index

	def test_index_inc(self):
		self.test_index = self.test_index + 1

	def set_max(self,x):
		self.max = x
	#	print "set_status:",status

	def get_max(self):
		return self.max

	def set_index(self,x):
		self.index = x
	#	print "set_status:",status

	def add_index(self,x):
		self.index = self.index + x

	def get_index(self):
		return self.index

	def update_index(self,count_f):
		self.add_index(2)
		count_f(0)
		if self.index == self.max:
			self.set_index(0)
			self.test_index_inc()

	def init_cmds(self,file_name):
		cmd_len = len(open(file_name,'rU').readlines())
		self.set_max(cmd_len)
		f = open(file_name,'rU')
		self.cmds =f.readlines()
		#print self.cmds
		f.close()
		print "clicker_test_cmd len = ",cmd_len/2

	def get_cmd_des(self):
		i = self.get_index()
		return self.cmds[i]

	def get_cmd_data(self,count_f):
		i = self.get_index()
		self.update_index(count_f)
		return self.cmds[i+1]