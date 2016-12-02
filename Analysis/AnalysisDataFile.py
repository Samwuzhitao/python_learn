#! /usr/bin/env python
#coding:utf-8
"""\
uart_message for serial ports.

"""
import os
import string

uid_init_flg        = 0
uidshowindex        = 0
uidshowflg          = 0
UID_SHOW_COL_NUM    = 5
UID_LOST_COUNT      = 0
UID_OK_COUNT        = 0
UID_MAX_COUNT       = 0
UID_COUNT           = 0
UID_STATISTIC_INDEX = 1
WHITE_LIST_LEN      = 120
UID_CMD_START_ADDR  = 8

def message_status_check(str):
	global uartm

	status = string.atoi(str, 10)
	if status == 0:
		show_str  = uartm.cmdindex + " Successed"
	else:
		show_str  = uartm.cmdindex + " Fail"
	return show_str

def message_status_check1(str):
	status = string.atoi(str, 10)
	if status == 0:
		str1 = " Ok"
	else:
		str1 = " Busy"
	return str1

def message_process_show(x,show_f):
	global UID_STATISTIC_INDEX

	show_str = " "
	show_f(show_str,'a')

	if x == 1:
		show_str = "Statistic : %d" % UID_STATISTIC_INDEX
		show_f(show_str,'a')
		show_str = "First Statistic:"
		show_f(show_str,'a')
		UID_STATISTIC_INDEX = UID_STATISTIC_INDEX + 1
	if x == 2:
		show_str = "Second Statistic:"
		show_f(show_str,'a')
	if x == 3:
		show_str = "Third Statistic:"
		show_f(show_str,'a')
	if x == 4:
		show_str = "Fourth Statistic:"
		show_f(show_str,'a')

def message_show_cmd_10(len,str,show_f):
	#print "message_show_cmd_10"
	global uartm

	if str[0:2] == "00":
		show_str  = uartm.cmdindex + "SEND DATA : Ok "
	if str[0:2] == "01":
		show_str  = uartm.cmdindex + "SEND DATA : Fail"

	show_str += " WL_FILTER_STATUS = "+str[3:5]
	uidlen   = string.atoi(str[6:8],16)
	show_str += " WL_LEN = %d" % uidlen
	show_f(show_str,'a')

def message_show_cmd_11(len,str,show_f):
	#print "message_show_cmd_10"
	global uartm
	#print ' Message : ' + str
	uartm.clicker_message_show(str)

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

def message_show_cmd_26(len,str,show_f):
	#print "message_show_cmd_26"
	global uartm

	uid = str[3:14]
	uid = uid.replace(' ','')
	show_str  = uartm.cmdindex + 'uPOS:[%3d] ' % string.atoi(str[0:2], 16)
	show_str += 'uID:[' + uid + ']'  + " Student Id:" + str[15:]
	show_f(show_str,'a')
	uartm.add(str[0:2]+uid)
	uartm.uids_data[uid] = []

def message_show_cmd_27(len,str,show_f):
	#print "message_show_cmd_27"
	show_f(message_status_check(str[0:2]),'a')

def message_show_cmd_28(len,str,show_f):
	#print "message_show_cmd_28"
	show_f(message_status_check(str[0:2]),'a')

def message_show_cmd_2a(len,str,show_f):
	#print "message_show_cmd_2a"
	show_f(message_status_check(str[0:2]),'a')

def message_show_cmd_2b(len,str,show_f):
	#print "message_show_cmd_2b"
	#print str
	global uidshowindex
	global uidshowflg

	uidlen   = string.atoi(str[0:2],16)
	show_str = " uid sum : %d " % uidlen
	show_f(show_str,'a')

	if uidshowflg == 0:
		uidshowindex = 0
		uidshowflg   = 1

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
	global UID_LOST_COUNT
	global uid_init_flg
	global uartm

 	if string.atoi(str[0:3], 16) == 1:
 		if uid_init_flg == 2:
 			uid_init_flg = 0

	message_process_show(string.atoi(str[0:3], 16),show_f)

 	UID_LOST_COUNT = (len/5)

	show_str =  uartm.cmdindex + "lost:"
	show_f(show_str,'a')
	i = 1
	j = 0
	show_str = ""
	while i < len-3 :
		uid = str[(i)*3:(i+5)*3-1]
		uid = uid.replace(' ','')
		i = i + 5
		show_str += "[%3d].%s " % (string.atoi(uid[0:2], 16),uid[2:])
		if uid_init_flg != 2:
			uartm.add(uid)
			uartm.uids_data[uid[2:]] = []
		j = j + 1
		if j == 5 :
			j = 0
			show_f(show_str,'a')
			show_str = ""
		if i >= len-3 :
			show_f(show_str,'a')
			show_str = ""
	if uid_init_flg == 0:
		uid_init_flg = 1

	#show_str = "count:%d" % (len/5)
	#show_f(show_str,'a')

def message_show_cmd_31(len,str,show_f):
	#print "message_show_cmd_31"
	#message_process_show(string.atoi(str[0:3], 16),show_f)
	global UID_LOST_COUNT
	global UID_OK_COUNT
	global UID_MAX_COUNT
	global UID_COUNT
	global uid_init_flg
	global uartm

 	UID_OK_COUNT  = (len/5)
 	UID_COUNT    += UID_OK_COUNT

 	if string.atoi(str[0:3], 16) == 1:
 		UID_MAX_COUNT = UID_LOST_COUNT + UID_OK_COUNT

	show_str =  uartm.cmdindex + "Ok:"
	show_f(show_str,'a')
	i = 1
	j = 0
	show_str = ""
	while i < len - 3:
		uid = str[(i)*3:(i+5)*3-1]
		uid = uid.replace(' ','')
		i = i + 5
		show_str += "[%3d].%s " % (string.atoi(uid[0:2], 16),uid[2:])
		if uid_init_flg != 2:
			uartm.add(uid)
			uartm.uids_data[uid[2:]] = []
		j = j + 1
		if j == 5 :
			j = 0
			show_f(show_str,'a')
			show_str = ""
		if i >= len-3 :
			show_f(show_str,'a')
			show_str = ""

	if uid_init_flg == 1:
		uid_init_flg = 2

	show_str = "count:%d" % (len/5)
	show_f(show_str,'a')

	if UID_MAX_COUNT == UID_COUNT:
		show_str = "Sum count:%d" % UID_MAX_COUNT
		show_f(show_str,'a')
		UID_COUNT = 0

def message_show_cmd_43(len,str,show_f):
	#print "message_show_cmd_30"
	show_str = "online uid:"
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

def message_show_cmd_a0(len,str,show_f):
	#print "message_show_cmd_a0"
	show_f(message_status_check(str[0:2]),'a')
	#show_str = " err code = "+str[3:5]
	#show_f(show_str,'a')
	#print str

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

def clicker_cmd_show(len,sign,str,show_f):
	#print "clicker_cmd_show"
	global uartm

	uid = sign.replace(' ','')
	is_white_list_uid = uartm.check(uid)
	if is_white_list_uid == True:
		show_str = uartm.cmdindex + 'uPOS:[%3d] ' % string.atoi(uartm.uidpos, 16) + 'uID:[' + uid + ']'  + " DATA:" + str
		uartm.uids_data[uid].append(show_str)
		#uartm.uids_data[uid] = '  ' + show_str
		show_f(show_str,'a')
	else:
		show_str  =  uartm.cmdindex + "UNKNOW UID : " + uid
		#show_str += 'uPOS:[%3d] ' % string.atoi(uartm.uidpos, 16) + 'uID:[' + uid + ']'
		show_f(show_str,'a')

def clicker_cmd_14(len,sign,str,show_f):
	#print "clicker_cmd_14"
	global uartm

	uid = sign.replace(' ','')
	is_white_list_uid = uartm.check(uid)
	if is_white_list_uid == True:
		show_str = uartm.cmdindex + 'uPOS:[%3d] ' % string.atoi(uartm.uidpos, 16) + 'uID:[' + uid + ']'
		if str[0:2] == '01':
			show_str += ' Power : ON'
		if str[0:2] == '02':
			show_str += ' Power : OFF'
		if str[0:2] == '03':
			show_str += ' Power : WakeUp'
		show_f(show_str,'a')

# import user module
class UartRevicer():
	def __init__(self,file_name):
		self.uids                    = []
		self.uids_data               = {}
		self.uid_len                 = 0
		self.uidpos                  = ""
		self.analysispath            = ""
		self.store_switch            = 1
		self.Count                   = [ 0, 0, 0, 0 ]
		self.cmdindex                = ""
		self.ReviceFunSets           = {
			"10":message_show_cmd_10,"11":message_show_cmd_11,
			"12":message_show_cmd_12,
			"20":message_show_cmd_20,"21":message_show_cmd_21,
			"22":message_show_cmd_22,"23":message_show_cmd_22,
			"24":message_show_cmd_22,"25":message_show_cmd_22,
			"26":message_show_cmd_26,"27":message_show_cmd_27,
			"28":message_show_cmd_28,"29":message_show_cmd_26,
			"2A":message_show_cmd_2a,"2B":message_show_cmd_2b,
			"2C":message_show_cmd_2c,"2D":message_show_cmd_22,
			"2E":message_show_cmd_2e,"2F":message_show_cmd_2f,
			"30":message_show_cmd_30,"31":message_show_cmd_31,
			"40":message_show_cmd_22,
			"41":message_show_cmd_22,"42":message_show_cmd_26,
			"43":message_show_cmd_43,
			"A0":message_show_cmd_a0,
			"FD":message_show_cmd_fd,
			"FE":message_show_cmd_fe,
			"FF":message_show_cmd_ff,
		}
		self.ClickerFunSets           = {
			"00":clicker_cmd_show,"10":clicker_cmd_show,
			"11":clicker_cmd_show,"12":clicker_cmd_show,
			"13":clicker_cmd_show,"14":clicker_cmd_14,
			"15":clicker_cmd_show,"16":clicker_cmd_show,
			"17":clicker_cmd_show,"19":clicker_cmd_show,
			"20":clicker_cmd_show,"21":clicker_cmd_show,
		}
		f = open(file_name,'rU')
		self.filelines  = f.readlines()
		f.close()
		print "Test file name: " + file_name
		print "Test file len : ",len(self.filelines)

	def add(self, uid):
		self.uids.append(uid)
		self.uid_len += 1

	def check(self,uid):
		for i in range(0,self.uid_len):
			if uid == self.uids[i][2:]:
				self.uidpos =  self.uids[i][0:2]
				return True
		return False

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
			f = open(self.analysispath,mode)
			print >> f, str
			f.close()

	def message_show(self,str):
		global uidshowflg
		cmdindex = str[0:UID_CMD_START_ADDR]
		cmddata  = str[UID_CMD_START_ADDR:]

		cmd_type = cmddata[3:5]
		len_str  = cmddata[18:20]
		len_int  = string.atoi(len_str, 16)
		data     = cmddata[21:21+len_int*3]
		xor      = cmddata[21+len_int*3:21+len_int*3+2]

		if cmd_type != "2b":
			uidshowflg = 0
		self.cmdindex = cmdindex
		self.ReviceFunSets[cmd_type](len_int,data,self.show)

	def clicker_message_show(self,str):
		sign     = str[3:14]
		rfu      = str[15:17]
		cmd_type = str[18:20]
		len_str  = str[21:23]
		len_int  = string.atoi(len_str, 16)
		data     = str[24:24+len_int*3]
		xor      = str[24+len_int*3:24+len_int*3+2]
		end      = str[24+(len_int+1)*3:24+(len_int+1)*3+2]

		self.ClickerFunSets[cmd_type](len_int,sign,data,self.show)

	def decode_file(self):
		for line in self.filelines:
			if line[0+UID_CMD_START_ADDR:2+UID_CMD_START_ADDR] == '5C':
				self.message_show(line)

if __name__=='__main__':
	# get file path
	path = os.path.abspath("./")

	# get the cmd num of the file 'testfile.txt'
	file_path = path + '\\AlignmentDataFile.txt'
	uartm = UartRevicer(file_path)
	uartm.analysispath = path + '\\AnalysisHexResult.txt'
	show_str =  "Test result analysis:"
	uartm.show(show_str,'w')
	uartm.decode_file()

	show_str =  "THE LAST PUSH DATA:"
	uartm.show(show_str,'a')

	index = 1
	for key in uartm.uids_data:
		show_str  = " <%3d> uID: " % index + key
		show_str += ", Count : %3d" % len(uartm.uids_data[key]) + ", List : "
		index = index + 1
		uartm.show(show_str,'a')
		itemindex = 1
		for item in uartm.uids_data[key]:
			show_str =  "\t[%3d]" % itemindex + item
			itemindex = itemindex + 1
			uartm.show(show_str,'a')