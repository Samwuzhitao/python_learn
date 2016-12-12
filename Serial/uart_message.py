#! /usr/bin/env python
#coding:utf-8
"""\
uart_message for serial ports.

"""
import string
import uart_whitelist
import time
from time import sleep

uidshowindex          = 0
g_pac_num             = 0
g_seq_num             = 0
store_uid_switch      = 0
uid_table_first_write = 0
UID_SHOW_COL_NUM      = 5
MESSAGE_HEADER_LEN    = 1
MESSAGE_DSTID_LEN     = 4
MESSAGE_SRCID_LEN     = 4
MESSAGE_PACKNUM_LEN   = 1
MESSAGE_SEQNUM_LEN    = 1
MESSAGE_PACKTYPE_LEN  = 1
MEAAAGE_CMD_LEN       = 1
MESSAGE_REVICED_LEN   = 2
MESSAGE_LEN_LEN       = 1
MESSAGE_XOR_LEN       = 1
MESSAGE_END_LEN       = 1

def message_status_check(str):
	ISOTIMEFORMAT = ' [ %Y-%m-%d %H:%M:%S ]'
	now = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
	status = string.atoi(str, 10)
	if status == 0:
		str1 = now + " OK"
	else:
		str1 = now + " FAIL"
	return str1

def message_err_check(str):
	status = string.atoi(str, 16)
	if status == 0:
		str1 = " OK"
	if status == 1:
		str1 = " LEN ERR"
	if status == 2:
		str1 = " PARAMETER ERR"
	return str1

def message_process_show(x,show_f):
	if x == 1:
		show_str = "First Statistic:"
		show_f(show_str,'a')
	if x == 2:
		show_str = "Second Statistic:"
		show_f(show_str,'a')
	if x == 3:
		show_str = "Third Statistic:"
		show_f(show_str,'a')
	if x == 4:
		show_str = "Fourth Statistic:"
		show_f(show_str,'a')

def message_show_cmd_10(packnum,seqnum,acktype,len,str,show_f):
	#print "message_show_cmd_10"
	show_f(message_status_check(str[0:2]),'a')
	show_str = " WL_FILTER_STATUS = "+str[3:5]
	uidlen   = string.atoi(str[6:8],16)
	show_str += " WL_LEN = %d" % uidlen
	show_f(show_str,'a')
	#print str

def message_decode_clicker_setting(packnum,seqnum,acktype,len,str,show_f):
	#print "message_show_cmd_10"
	cmdtype = str[0:2]
	str = str[3:]

	ISOTIMEFORMAT = ' [ %Y-%m-%d %H:%M:%S ]'
	now = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )

	if (cmdtype == "01"):
		desc = " G_ONOFF   : "
	if (cmdtype == "02"):
		desc = " G_POWER   : "
	if (cmdtype == "03"):
		desc = " G_DISP    : "
	if (cmdtype == "04"):
		desc = " N_CH      : "
	if (cmdtype == "05"):
		desc = " N_TIME    : "
	if (cmdtype == "06"):
		desc = " N_READ_ID : "
	if (cmdtype == "07"):
		desc = " N_WR_EE   : "
	if (cmdtype == "08"):
		desc = " N_RD_EE   : "

	show_str = now + desc + message_err_check(str)
	show_f(show_str,'a')


def message_show_cmd_22(packnum,seqnum,acktype,len,str,show_f):
	#print "message_show_cmd_22:white list init "
	show_f(message_status_check(str[0:2]),'a')

def message_show_cmd_26(packnum,seqnum,acktype,len,str,show_f):
	#print "message_show_cmd_26"
	ISOTIMEFORMAT = ' [ %Y-%m-%d %H:%M:%S ]'
	now = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
	uid = str[3:14]
	uid = uid.replace(' ','')
	show_str  = now + ' uPOS:[%3d] ' % string.atoi(str[0:2], 16)
	show_str += 'uID:[' + uid + ']'  + " Student ID:" + str[15:]
	show_f(show_str,'a')

def message_decode_uid_cmd_result(packnum,seqnum,acktype,len,str,show_f):
	#print "message_show_cmd_2b"
	#print str
	global uidshowindex
	global g_pac_num
	global g_seq_num
	global store_uid_switch
	global uid_table_first_write

	cmdtype = str[0:2]
	str = str[3:]

	ISOTIMEFORMAT = ' [ %Y-%m-%d %H:%M:%S ]'
	now = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )

	if (cmdtype == "04"):
		show_f(message_status_check(str[0:2]),'a')
		uidlen   = string.atoi(str[3:],16)
		show_str = " WL_LEN = %d" % uidlen
		show_f(show_str,'a')
		return

	if (cmdtype == "01") | (cmdtype == "02"):
		okcount   = string.atoi(str[0:2],16)
		show_str = now + " WL_OK_COUNT = %d" % okcount
		uidlen   = string.atoi(str[3:5],16)
		show_str += " WL_LEN = %d" % uidlen
		show_str += " WL_DETAIL = "+str[6:]
		show_f(show_str,'a')
		return

	if cmdtype == "03":
		if packnum != g_pac_num:
			uidshowindex = 0
			store_uid_switch = 0
			uidlen   = string.atoi(str[0:2],16)
			show_str = now + " uID SUM : %d " % uidlen
			show_f(show_str,'a')
			g_pac_num = packnum
			if seqnum != g_seq_num:
				store_uid_switch = 1
				g_pac_num = seqnum
		else:
			show_str = now
			show_f(show_str,'a')

		i = 0
		j = 0
		show_str = " "

		while i < len :
			uid = str[(i+1)*3:(i+6)*3-1]
			uid = uid.replace(' ','')
			i = i + 5
			if uid != "":
				show_str     += "[%3d].%s " % (string.atoi(uid[0:2],16),uid[2:])
				uidshowindex = uidshowindex + 1
				j = j + 1
			if j == UID_SHOW_COL_NUM:
				j = 0
				show_f(show_str,'a')
				show_str = " "
			if i >= len :
				show_f(show_str,'a')
				show_str = " "
		uid_table_first_write = 0
		return

def message_decode_systick_cmd_result(packnum,seqnum,acktype,len,str,show_f):
	#print "message_show_cmd_2c"
	ISOTIMEFORMAT = ' [ %Y-%m-%d %H:%M:%S ]'
	now = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
	show_str  = now
	if acktype == 0x01:
		show_f(show_str,'a')
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
	else:
		err = str[0:2]
		show_str = show_str + " Err Type: " + err
		show_f(show_str,'a')

def message_show_cmd_2d(packnum,seqnum,acktype,len,str,show_f):
	#print "message_show_cmd_2d"
	i = 0
	while i < len :
		uid      = str[(i)*3:(i+4)*3-1]
		show_str = " online uid %2d : %s " % (i/4,uid)
		show_f(show_str,'a')
		i = i + 4

def message_show_cmd_2e(packnum,seqnum,acktype,len,str,show_f):
	#print "message_show_cmd_2e"
	str = str.replace(' ','')
	show_str = " Src uid :"+str
	show_f(show_str,'a')

def message_show_cmd_2f(packnum,seqnum,acktype,len,str,show_f):
	#print "message_show_cmd_2f"
	show_f(message_status_check(str[0:2]),'a')

def message_show_cmd_30(packnum,seqnum,acktype,len,str,show_f):
	#print "message_show_cmd_30"
	message_process_show(string.atoi(str[0:3], 16),show_f)
	show_str = "lost:"
	show_f(show_str,'a')
	i = 1
	j = 0
	show_str = ""
	while i < len-3 :
		uid = str[(i)*3:(i+5)*3-1]
		uid = uid.replace(' ','')
		i = i + 5
		show_str += "[%3d].%s " % (string.atoi(uid[0:2], 16),uid[2:])
		j = j + 1
		if j == 5 :
			j = 0
			show_f(show_str,'a')
			show_str = ""
		if i >= len-3 :
			show_f(show_str,'a')
			show_str = ""
	show_str = "count:%d" % (len/5)
	show_f(show_str,'a')

def message_show_cmd_31(packnum,seqnum,acktype,len,str,show_f):
	#print "message_show_cmd_31"
	message_process_show(string.atoi(str[0:3], 16),show_f)
	show_str = "Ok:"
	show_f(show_str,'a')
	i = 1
	j = 0
	show_str = ""
	while i < len - 3:
		uid = str[(i)*3:(i+5)*3-1]
		uid = uid.replace(' ','')
		i = i + 5
		show_str += "[%3d].%s " % (string.atoi(uid[0:2], 16),uid[2:])
		j = j + 1
		if j == 5 :
			j = 0
			show_f(show_str,'a')
			show_str = ""
		if i >= len-3 :
			show_f(show_str,'a')
			show_str = ""

	show_str = "count:%d" % (len/5)
	show_f(show_str,'a')

def message_show_cmd_43(packnum,seqnum,acktype,len,str,show_f):
	#print "message_show_cmd_30"
	ISOTIMEFORMAT = ' [ %Y-%m-%d %H:%M:%S ]'
	now = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
	show_str = now + " Online uID:"
	show_f(show_str,'a')
	i = 0
	j = 0
	show_str = ""
	while i < len-3 :
		uid = str[(i)*3:(i+5)*3-1]
		uid = uid.replace(' ','')
		i = i + 5
		show_str += "[%3d].%s " % (string.atoi(uid[0:2], 16),uid[2:])
		j = j + 1
		if j == 5 :
			j = 0
			show_f(show_str,'a')
			show_str = ""
		if i >= len-3 :
			show_f(show_str,'a')
			show_str = ""
	show_str = "count:%d" % (len/5)
	show_f(show_str,'a')

def message_Err(packnum,seqnum,acktype,len,str,show_f):
	#print "message_show_cmd_fd"
	show_str = message_status_check(str[0:2]) + " err code = "+str[3:5]
	show_f(show_str,'a')

# import user module
class UartM():
	def __init__(self):
		self.cmd_file_path           = ""
		self.statistical_result_path = ""
		self.detailed_result_path    = ""
		self.uid_table_path          = ""
		self.store_switch            = 0
		self.ack_type                = 0
		self.seq_num                 = 0
		self.pac_num                 = 0
		self.Count                   = [ 0, 0, 0, 0 ]
		self.ReviceFunSets           = {
			"10":message_show_cmd_10,
			"11":message_decode_clicker_setting,
			"12":message_decode_uid_cmd_result,
			"13":message_decode_systick_cmd_result,
			"14":message_Err,
		}

	def set_detailed_file(self,str):
		self.detailed_result_path = str

	def set_statistical_path(self,str):
		self.statistical_result_path = str

	def set_cmd_path(self,str):
		self.cmd_file_path = str

	def set_uid_table_path(self,str):
		self.uid_table_path = str

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
		global store_uid_switch
		global uid_table_first_write

		switch = self.get_store_switch()

		if switch == 1:
			f = open(self.detailed_result_path,'a')
			print >> f, str
			f.close()
		if store_uid_switch == 1:
			if uid_table_first_write == 0:
				f = open(self.uid_table_path,'w')
				uid_table_first_write = 1
			else:
				f = open(self.uid_table_path,'a')
			print >> f, str
			f.close()
		print str

	def message_show(self,str):
		#print str
		# header
		startaddr = 1
		endaddr   = MESSAGE_HEADER_LEN*3
		#show_str = "HEAD     = "+str[startaddr:endaddr]
		#self.show(show_str,'a')

		# dstid
		startaddr = endaddr + 1
		endaddr   = endaddr + MESSAGE_DSTID_LEN*3
		dstid     = str[startaddr:endaddr]
		#show_str = "DISID    = "+dstid
		#self.show(show_str,'a')

		#srcid
		startaddr = endaddr + 1
		endaddr   = endaddr + MESSAGE_SRCID_LEN*3
		srcid     = str[startaddr:endaddr]
		#show_str = "SRCID    = "+srcid
		#self.show(show_str,'a')

		#packnum MESSAGE_PACKNUM_LEN   = 1
		startaddr = endaddr + 1
		endaddr   = endaddr + MESSAGE_PACKNUM_LEN*3
		packnum   = str[startaddr:endaddr]
		self.pac_num = string.atoi(packnum, 16)
		#show_str = "PACKNUM  = "+packnum
		#self.show(show_str,'a')

		#seqnum MESSAGE_SEQNUM_LEN    = 1
		startaddr = endaddr + 1
		endaddr   = endaddr + MESSAGE_SEQNUM_LEN*3
		seqnum    = str[startaddr:endaddr]
		self.seq_num = string.atoi(seqnum, 16)
		#show_str = "PACKNUM  = "+seqnum
		#self.show(show_str,'a')

		#seqnum MESSAGE_PACKTYPE_LEN    = 1
		startaddr = endaddr + 1
		endaddr   = endaddr + MESSAGE_PACKTYPE_LEN*3
		packtype  = str[startaddr:endaddr]
		self.ack_type = string.atoi(packtype, 16)
		#show_str = "PACKTYPE = "+packtype
		#self.show(show_str,'a')

		#seqnum MEAAAGE_CMD_LEN       = 1
		startaddr = endaddr + 1
		endaddr   = endaddr + MEAAAGE_CMD_LEN*3
		cmd       = str[startaddr:endaddr]
		#show_str = "CMD      = "+cmd
		#self.show(show_str,'a')

		#seqnum MESSAGE_REVICED_LEN   = 2
		startaddr = endaddr + 1
		endaddr   = endaddr + MESSAGE_REVICED_LEN*3
		reviced   = str[startaddr:endaddr]
		#show_str = "REVICED  = "+reviced
		#self.show(show_str,'a')

		#seqnum MESSAGE_LEN_LEN       = 1
		startaddr = endaddr + 1
		endaddr   = endaddr + MESSAGE_LEN_LEN*3
		len_str   = str[startaddr:endaddr]
		#show_str = "LEN      = "+len_str
		#self.show(show_str,'a')
		len_int   = string.atoi(len_str, 16)
		#print len_int

		# data 
		startaddr = endaddr + 1
		endaddr   = endaddr + len_int*3
		data      = str[startaddr:endaddr]
		#show_str = "DATA     = "+data
		#self.show(show_str,'a')

		# xor MESSAGE_XOR_LEN       = 1
		startaddr = endaddr + 1
		endaddr   = endaddr + MESSAGE_XOR_LEN*3
		xor       =  str[startaddr:endaddr]
		#show_str = "XOR      = "+xor
		#self.show(show_str,'a')

		# end MESSAGE_END_LEN       = 1
		startaddr = endaddr + 1
		endaddr   = endaddr + MESSAGE_END_LEN*3
		end       = str[startaddr:endaddr]
		#show_str = "END      = "+end
		#self.show(show_str,'a')

		self.ReviceFunSets[cmd](self.pac_num,self.seq_num,self.ack_type,len_int,data,self.show)

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
