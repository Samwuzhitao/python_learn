#! /usr/bin/env python
#coding:utf-8
"""\
uart_message for serial ports.

"""
import string
import uart_whitelist

uidshowindex     = 0
uidshowflg       = 0
UID_SHOW_COL_NUM = 5

def message_status_check(str):
	status = string.atoi(str, 10)
	if status == 0:
		str1 = " Successed"
	else:
		str1 = " Fail"
	return str1

def message_status_check1(str):
	status = string.atoi(str, 10)
	if status == 0:
		str1 = " Ok"
	else:
		str1 = " Busy"
	return str1

def message_show_cmd_10(len,str,show_f):
	#print "message_show_cmd_10"
	show_f(message_status_check1(str[0:2]),'a')
	show_str = " whitelist: state = "+str[3:5]
	uidlen   = string.atoi(str[6:8],16)
	show_str += " len = %d" % uidlen
	show_f(show_str,'a')

def message_show_cmd_12(len,str,show_f):
	#print "message_show_cmd_12"
	show_f(message_status_check(str[0:2]),'a')
	show_str = " whitelist: state = "+str[3:5]
	uidlen   = string.atoi(str[6:8],16)
	show_str += " len = %d" % uidlen
	show_f(show_str,'a')

def message_show_cmd_20(len,str,show_f):
	#print "message_show_cmd_20"
	uidlen   = string.atoi(str[0:2],16)
	show_str = " ok = %d" % uidlen
	uidlen   = string.atoi(str[27:29],16)
	show_str += " len = %d" % uidlen
	show_f(show_str,'a')
	show_str = " detail state = "+str[3:26]
	show_f(show_str,'a')

def message_show_cmd_21(len,str,show_f):
	#print "message_show_cmd_21"
	uidlen   = string.atoi(str[0:2],16)
	show_str = " ok = %d" % uidlen
	uidlen   = string.atoi(str[27:29],16)
	show_str += " len = %d" % uidlen
	show_f(show_str,'a')
	show_str = " detail state = "+str[3:26]
	show_f(show_str,'a')

def message_show_cmd_22(len,str,show_f):
	#print "message_show_cmd_22:white list init "
	show_f(message_status_check(str[0:2]),'a')

def message_show_cmd_23(len,str,show_f):
	#print "message_show_cmd_22"
	show_f(message_status_check(str[0:2]),'a')

def message_show_cmd_24(len,str,show_f):
	#print "message_show_cmd_23"
	show_f(message_status_check(str[0:2]),'a')

def message_show_cmd_25(len,str,show_f):
	#print "message_show_cmd_25"
	show_f(message_status_check(str[0:2]),'a')

def message_show_cmd_26(len,str,show_f):
	#print "message_show_cmd_26"
	show_str = " new uid = "+str[0:11]
	show_f(show_str,'a')

def message_show_cmd_27(len,str,show_f):
	#print "message_show_cmd_27"
	show_f(message_status_check(str[0:2]),'a')

def message_show_cmd_28(len,str,show_f):
	#print "message_show_cmd_28"
	show_f(message_status_check(str[0:2]),'a')

def message_show_cmd_29(len,str,show_f):
	#print "message_show_cmd_29"
	show_str = " new uid = "+str[0:11]
	show_f(show_str,'a')

def message_show_cmd_2a(len,str,show_f):
	#print "message_show_cmd_2a"
	show_f(message_status_check(str[0:2]),'a')

def message_show_cmd_2b(len,str,show_f):
	#print "message_show_cmd_2b"
	#print str
	global uidshowindex
	global uidshowflg

	uidlen   = string.atoi(str[0:2],16)
	show_str = " read uid sum index : %d " % uidlen
	show_f(show_str,'a')

	if uidshowflg == 0:
		uidshowindex = 0
		uidshowflg   = 1

	i = 0
	j = 0
	show_str = " "

	while i < len :
		uid = str[(i+1)*3:(i+5)*3-1]
		uid = uid.replace(' ','')
		i = i + 4
		if uid != "":
			show_str     += "[%3d].%s " % (uidshowindex,uid)
			uidshowindex = uidshowindex + 1
			j = j + 1
		if j == UID_SHOW_COL_NUM:
			j = 0
			show_f(show_str,'a')
			show_str = " "
		if i >= len :
			show_f(show_str,'a')
			show_str = " "

def message_show_cmd_2c(len,str,show_f):
	#print "message_show_cmd_2c"
	uid       = str[0:11]
	show_str  = " ID  = "+uid.replace(' ','')
	show_f(show_str,'a')
	sw_verion = str[12:20]
	sw_verion = sw_verion.replace(' ','')
	sw1 = string.atoi(sw_verion[0:2], 10)
	sw2 = string.atoi(sw_verion[2:6], 10)
	show_str  = " SW  = %d.%02d" % (sw1,sw2)
	show_f(show_str,'a')
	hwstr = str[21:65]
	hwstr = hwstr.replace(' ','')
	hwstr = hwstr.decode("hex")
	show_str  = " HW  = "+hwstr
	show_f(show_str,'a')
	comstr = str[66:]
	comstr = comstr.replace(' ','')
	comstr = comstr.decode("hex")
	show_str  = " COM = "+comstr
	show_f(show_str,'a')

def message_show_cmd_2d(len,str,show_f):
	#print "message_show_cmd_2d"
	i = 0
	while i < len :
		uid      = str[(i)*3:(i+4)*3-1]
		show_str = " online uid %2d : %s " % (i/4,uid)
		show_f(show_str,'a')
		i = i + 4

def message_show_cmd_2e(len,str,show_f):
	#print "message_show_cmd_2e"
	str = str.replace(' ','')
	show_str = " Src uid :"+str
	show_f(show_str,'a')

def message_show_cmd_2f(len,str,show_f):
	#print "message_show_cmd_2f"
	show_f(message_status_check(str[0:2]),'a')

def message_show_cmd_30(len,str,show_f):
	#print "message_show_cmd_30"
	show_str = "lost:"
	show_f(show_str,'a')
	i = 0
	j = 0
	show_str = " "
	while i < len :
		uid = str[(i)*3:(i+4)*3-1]
		uid = uid.replace(' ','')
		i = i + 4
		show_str += " %s " % uid
		j = j + 1
		if j == 5 :
			j = 0
			show_f(show_str,'a')
			show_str = " "
		if i >= len :
			show_f(show_str,'a')
			show_str = " "
	show_str = " count:%d" % (len/4)
	show_f(show_str,'a')

def message_show_cmd_31(len,str,show_f):
	#print "message_show_cmd_31"
	show_str = "Ok:"
	show_f(show_str,'a')
	i = 0
	j = 0
	show_str = " "
	while i < len :
		uid = str[(i)*3:(i+4)*3-1]
		uid = uid.replace(' ','')
		i = i + 4
		show_str += " %s " % uid
		j = j + 1
		if j == 5 :
			j = 0
			show_f(show_str,'a')
			show_str = " "
		if i >= len :
			show_f(show_str,'a')
			show_str = " "

	show_str = " count:%d" % (len/4)
	show_f(show_str,'a')

def message_show_cmd_fd(len,str,show_f):
	#print "message_show_cmd_fd"
	show_f(message_status_check(str[0:2]),'a')
	show_str = " err code = "+str[3:5]
	show_f(show_str,'a')

def message_show_cmd_fe(len,str,show_f):
	#print "message_show_cmd_fe"
	show_f(message_status_check(str[0:2]),'a')
	show_str = " err code = "+str[3:5]
	show_f(show_str,'a')

def message_show_cmd_ff(len,str,show_f):
	#print "message_show_cmd_ff"
	show_f(message_status_check(str[0:2]),'a')
	show_str = " err code = "+str[3:5]
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
			"10":message_show_cmd_10,"12":message_show_cmd_12,
			"20":message_show_cmd_20,"21":message_show_cmd_21,
			"22":message_show_cmd_22,"23":message_show_cmd_23,
			"24":message_show_cmd_24,"25":message_show_cmd_25,
			"26":message_show_cmd_26,"27":message_show_cmd_27,
			"28":message_show_cmd_28,"29":message_show_cmd_29,
			"2a":message_show_cmd_2a,"2b":message_show_cmd_2b,
			"2c":message_show_cmd_2c,"2d":message_show_cmd_2d,
			"2e":message_show_cmd_2e,"2f":message_show_cmd_2f,
			"30":message_show_cmd_30,"31":message_show_cmd_31,
			"fd":message_show_cmd_fd,
			"fe":message_show_cmd_fe,
			"ff":message_show_cmd_ff,
		}

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

	def message_show1(self,str):
		show_str = "HEADER = "+str[1:3]
		self.show(show_str,'a')
		cmd_type = str[4:6]
		show_str = "TYPE   = "+cmd_type
		self.show(show_str,'a')
		sign_str = str[7:18]
		show_str = "SIGN   = "+sign_str
		self.show(show_str,'a')
		len_str  = str[19:21]
		show_str = "LEN    = "+len_str
		self.show(show_str,'a')
		len_int  = string.atoi(len_str, 16)
		#print len_int
		data     = str[22:22+len_int*3]
		show_str = "DATA   = "+data
		self.show(show_str,'a')
		xor      = str[22+len_int*3:22+len_int*3+2]
		show_str = "XOR    = "+xor
		self.show(show_str,'a')
		end      = str[22+(len_int+1)*3:22+(len_int+1)*3+2]
		show_str = "END    = "+end
		self.show(show_str,'a')

		self.ReviceFunSets[cmd_type](len_int,data,self.show)

		show_str = " "
		self.show(show_str,'a')

	def message_show(self,str):
		global uidshowflg

		cmd_type = str[4:6]
		len_str  = str[19:21]
		len_int  = string.atoi(len_str, 16)
		data     = str[22:22+len_int*3]
		xor      = str[22+len_int*3:22+len_int*3+2]

		if cmd_type != "2b":
			uidshowflg = 0

		self.ReviceFunSets[cmd_type](len_int,data,self.show)
		show_str = " "
		self.show(show_str,'a')

	def store(self):
		f = open(self.statistical_result_path,'w')
		#print self.Count
		f.write('[TEST] send   cmd count = ' + hex(self.get_count(0)) + '\n')
		f.write('[TEST] revice cmd count = ' + hex(self.get_count(1)) + '\n')
		f.write('[TEST] ok     cmd count = ' + hex(self.get_count(2)) + '\n')
		f.write('[TEST] err    cmd count = ' + hex(self.get_count(3)) + '\n')
		f.close()
