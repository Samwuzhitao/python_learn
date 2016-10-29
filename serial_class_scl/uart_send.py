#! /usr/bin/env python
"""\
uart_send for serial ports.

"""
import ConfigParser
import os
import time
from time import sleep

class UartS():
	def __init__(self):
		self.TEST_MAX    = 0
		self.test_index  = 0
		self.index       = 0
		self.cmds        = []
		self.cmdlen      = 0
		self.usercmds    = []
		self.usercmdlen  = 0
		self.usercmdsel  = 0
		#self.SendFunSets = {
		#	7:whitelist_add,
		#	9:whitelist_delete,
		#}
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
		self.cmdlen = cmd_len/2
		print "clicker auto cmd len = ",cmd_len/2
		self.usercmdlen = 10
		self.usercmds = self.cmds[0:20]
		print "clicker user cmd len = ",self.usercmdlen

	def get_cmd_des(self):
		i = self.get_index()
		return self.cmds[i]

	def get_cmd_data(self,count_f):
		i = self.get_index()
		self.update_index(count_f)
		return self.cmds[i+1]

	def get_user_cmd(self):
		if self.usercmdsel == 7:
			print "7"
			return  self.usercmds[2*self.usercmdsel+1]

		if self.usercmdsel == 8:
			print "8"
			return  self.usercmds[2*self.usercmdsel+1]

		if ((self.usercmdsel != 8) & (self.usercmdsel != 7)):
			return  self.usercmds[2*self.usercmdsel+1]

	def get_user_des(self):
		self.usercmdsel = 0
		print " User cmd operation: "
		for i in range(0,self.usercmdlen):
			cmd = self.usercmds[2*i]
			cmd = cmd.strip('\n')
			if cmd[0:1] == "<":
				print " <%2d>" % i + cmd[10:]
			else:
				print " <%2d>" % i + cmd[6:]

		self.usercmdsel = input(' Please select your cmd ( 0 .. %d ): ' % (self.usercmdlen-1) )

		return  self.usercmds[2*self.usercmdsel]