#! /usr/bin/env python
#coding:utf-8
"""\
uart_message for serial ports.

"""
import os
import string

cmd_index = 0

# import user module
class UartDecode():
	def __init__(self,file_name):
		self.analysispath  = ""
		self.store_switch  = 1
		self.cmdline       = ""
		f = open(file_name,'rU')
		self.filelines  = f.readlines()
		f.close()
		print "Test file name: " + file_name
		print "Test file len : ",len(self.filelines)

	def set_store_switch(self,x):
		self.store_switch = x

	def get_store_switch(self):
		return self.store_switch

	def show(self,str,mode):
		switch = self.get_store_switch()
		print str
		if switch == 1:
			f = open(self.analysispath,mode)
			print >> f, str
			f.close()

	def decodefile(self,str):
		global cmd_index

		if len(str) > 21:
			len_str  = str[18:20]
			len_int  = string.atoi(len_str, 16)
			if ( 21+len_int*3+5 ) < len(str) :
				show_str = '<%5d> ' % cmd_index + str[0:21+len_int*3+5]
				cmd_index = cmd_index + 1
				self.show(show_str,'a')
				self.decodefile( str[21+len_int*3+6:])


	def decode_file(self):
		for line in self.filelines:
			self.decodefile(line)

if __name__=='__main__':
	# get file path 
	path = os.path.abspath("./")

	# get the cmd num of the file 'testfile.txt'
	file_path = path + '\\TestDataFile.txt'
	uartd = UartDecode(file_path)

	uartd.analysispath = path + '\\AlignmentDataFile.txt'
	show_str =  "Test result analysis:"
	uartd.show(show_str,'w')
	uartd.decode_file()