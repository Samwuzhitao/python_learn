#! /usr/bin/env python
"""\
Scan for serial ports.

Part of pySerial (http://pyserial.sf.net)
(C) 2002-2003 <cliechti@gmx.net>

The scan function of this module tries to open each port number
from 0 to 255 and it builds a list of those ports where this was
successful.
"""
import string

class Clicker():
	"""docstring for ClassName"""
	def __init__(self):
		self.uid = ""
		self.cnt = 0

def message_show_cmd_10(len,str,show_f):
	#print "message_show_cmd_10"
	if len/3 == 3:
		show_str = "operation state         = "+str[0:2]
		show_f(show_str,'a')
		show_str = "white list switch state = "+str[3:5]
		show_f(show_str,'a')
		show_str = "white list switch len   = "+str[6:8]
		show_f(show_str,'a')
	else:
		show_str = "clicker data is = "+str
		show_f(show_str,'a')

def message_show_cmd_12(len,str,show_f):
	#print "message_show_cmd_12"
	show_str = "operation state         = "+str[0:2]
	show_f(show_str,'a')
	show_str = "white list switch state = "+str[3:5]
	show_f(show_str,'a')
	show_str = "white list switch len   = "+str[6:8]
	show_f(show_str,'a')

def message_show_cmd_20(len,str,show_f):
	#print "message_show_cmd_20"
	show_str = "white list new uid count = "+str[0:2]
	show_f(show_str,'a')
	show_str = "white list add uid state = "+str[3:26]
	show_f(show_str,'a')
	show_str = "white list switch len    = "+str[27:29]
	show_f(show_str,'a')

def message_show_cmd_21(len,str,show_f):
	#print "message_show_cmd_21"
	show_str = "white list new uid count = "+str[0:2]
	show_f(show_str,'a')
	show_str = "white list add uid state = "+str[3:26]
	show_f(show_str,'a')
	show_str = "white list switch len    = "+str[27:29]
	show_f(show_str,'a')

def message_show_cmd_22(len,str,show_f):
	#print "message_show_cmd_22:white list init "
	show_str = "operation state = "+str[0:2]
	show_f(show_str,'a')

def message_show_cmd_23(len,str,show_f):
	#print "message_show_cmd_22"
	show_str = "operation state = "+str[0:2]
	show_f(show_str,'a')

def message_show_cmd_24(len,str,show_f):
	#print "message_show_cmd_23"
	show_str = "operation state = "+str[0:2]
	show_f(show_str,'a')

def message_show_cmd_25(len,str,show_f):
	#print "message_show_cmd_25"
	show_str = "operation state = "+str[0:2]
	show_f(show_str,'a')

def message_show_cmd_26(len,str,show_f):
	#print "message_show_cmd_26"
	show_str = "new uid         = "+str[0:11]
	show_f(show_str,'a')

def message_show_cmd_27(len,str,show_f):
	#print "message_show_cmd_27"
	show_str = "operation state = "+str[0:2]
	show_f(show_str,'a')

def message_show_cmd_28(len,str,show_f):
	#print "message_show_cmd_28"
	show_str = "operation state = "+str[0:2]
	show_f(show_str,'a')

def message_show_cmd_29(len,str,show_f):
	#print "message_show_cmd_29"
	show_str = "new uid         = "+str[0:11]
	show_f(show_str,'a')

def message_show_cmd_2a(len,str,show_f):
	#print "message_show_cmd_2a"
	show_str = "operation state = "+str[0:2]
	show_f(show_str,'a')

def message_show_cmd_2b(len,str,show_f):
	#print "message_show_cmd_2b"
	show_str = "read uid count  = "+str[0:2]
	show_f(show_str,'a')

	i = 0
	while i < len - 4:
		uid = str[(i+1)*3:(i+5)*3-1]
		show_str = "read uid %2d : %s " % (i/4,uid)
		show_f(show_str,'a')
		i = i + 4

def message_show_cmd_2c(len,str,show_f):
	#print "message_show_cmd_2c"
	uid       = str[0:11]
	show_str  = "uid             = "+uid
	show_f(show_str,'a')
	sw_verion = str[12:20]
	show_str  = "SW              = "+sw_verion
	show_f(show_str,'a')
	show_str  = "HW              = "+str[21:65]
	show_f(show_str,'a')
	show_str  = "COM             = "+str[66:]
	show_f(show_str,'a')

def message_show_cmd_2d(len,str,show_f):
	#print "message_show_cmd_2d"
	i = 0
	while i < len :
		uid = str[(i)*3:(i+4)*3-1]
		show_str = "online uid %2d : %s " % (i/4,uid)
		show_f(show_str,'a')
		i = i + 4

def message_show_cmd_2e(len,str,show_f):
	#print "message_show_cmd_2e"
	show_str = "revicer uid     = "+str[0:11]
	show_f(show_str,'a')

def message_show_cmd_2f(len,str,show_f):
	#print "message_show_cmd_2f"
	show_str = "operation state = "+str[0:2]
	show_f(show_str,'a')

def message_show_cmd_30(len,str,show_f):
	#print "message_show_cmd_30"
	if str[0:2] == "00":
		str1 = str[3:]
		show_str = "outline count : " + str[0:2]
		show_f(show_str,'a')
		i = 0
		while i < len-1 :
			uid = str1[(i)*3:(i+4)*3-1]
			show_str = "outline uid %2d : %s " % (i/4,uid)
			show_f(show_str,'a')
			i = i + 4

def message_show_cmd_fd(len,str,show_f):
	#print "message_show_cmd_fd"
	show_str = "operation state = "+str[0:2]
	show_f(show_str,'a')
	show_str = "err code        = "+str[3:5]
	show_f(show_str,'a')

def message_show_cmd_fe(len,str,show_f):
	#print "message_show_cmd_fe"
	show_str = "operation state = "+str[0:2]
	show_f(show_str,'a')
	show_str = "err code        = "+str[3:5]
	show_f(show_str,'a')

def message_show_cmd_ff(len,str,show_f):
	#print "message_show_cmd_ff"
	show_str = "operation state = "+str[0:2]
	show_f(show_str,'a')
	show_str = "err code        = "+str[3:5]
	show_f(show_str,'a')

# import user module
class UartM():
	def __init__(self):
		self.cmd_file_path           = ""
		self.statistical_result_path = ""
		self.detailed_result_path    = ""
		self.store_switch            = 0
		self.Count                   = [ 0, 0, 0, 0 ]
		self.ReviceFunSets           = {
			"10":message_show_cmd_10,
			"12":message_show_cmd_12,
			"20":message_show_cmd_20,
			"21":message_show_cmd_21,
			"22":message_show_cmd_22,
			"23":message_show_cmd_23,
			"24":message_show_cmd_24,
			"25":message_show_cmd_25,
			"26":message_show_cmd_26,
			"27":message_show_cmd_27,
			"28":message_show_cmd_28,
			"29":message_show_cmd_29,
			"2a":message_show_cmd_2a,
			"2b":message_show_cmd_2b,
			"2c":message_show_cmd_2c,
			"2d":message_show_cmd_2d,
			"2e":message_show_cmd_2e,
			"2f":message_show_cmd_2f,
			"30":message_show_cmd_30,
			"fd":message_show_cmd_fd,
			"fe":message_show_cmd_fe,
			"ff":message_show_cmd_ff,
		}
#		self.fun5aSets               = {
#			"10":message_show_5a_cmd_10,
#		}
		#print "UartM Class init Ok!"

	def set_detailed_file(self,str):
		self.detailed_result_path = str

	def set_statistical_path(self,str):
		self.statistical_result_path = str

	def set_cmd_path(self,str):
		self.cmd_file_path = str

	def set_store_switch(self,x):
		self.store_switch = x

	def get_store_switch(self):
		return self.store_switch

	def set_count(self,i,x):
		self.Count[i] = x

	def get_count(self,i):
		return self.Count[i]

	def count_inc(self,i):
		self.Count[i] = self.Count[i] + 1

	def show(self,str,mode):
		switch = self.get_store_switch()
		print str
		if switch == 1:
			f = open(self.detailed_result_path,mode)
			print >> f, str
			f.close()

	def message_show(self,str):
		show_str = "Message->HEADER = "+str[1:3]
		self.show(show_str,'a')
		cmd_type = str[4:6]
		show_str = "Message->TYPE   = "+cmd_type
		self.show(show_str,'a')
		sign_str = str[7:18]
		show_str = "Message->SIGN   = "+sign_str
		self.show(show_str,'a')
		len_str = str[19:21]
		show_str = "Message->LEN    = "+len_str
		self.show(show_str,'a')
		len_int = string.atoi(len_str, 16)
		#print len_int
		data = str[22:22+len_int*3]
		show_str = "Message->DATA   = "+data
		self.show(show_str,'a')
		xor = str[22+len_int*3:22+len_int*3+2]
		show_str = "Message->XOR    = "+xor
		self.show(show_str,'a')
		end = str[22+(len_int+1)*3:22+(len_int+1)*3+2]
		show_str = "Message->END    = "+end
		self.show(show_str,'a')

		self.ReviceFunSets[cmd_type](len_int,data,self.show)

		show_str = "\n"
		self.show(show_str,'a')

	def store(self):
		f = open(self.statistical_result_path,'w')
		#print self.Count
		f.write('[TEST] send cmd count          = ' + hex(self.get_count(0)) + '\n')
		f.write('[TEST] test instructions count = ' + hex(self.get_count(1)) + '\n')
		f.write('[TEST] ok  instructions count  = ' + hex(self.get_count(2)) + '\n')
		f.write('[TEST] err instructions count  = ' + hex(self.get_count(3)) + '\n')
		f.close()


