#! /usr/bin/env python
#coding:utf-8
"""\
uart_whitelist for serial ports.

"""
import string
import sys
import os
from time import sleep

WHITE_LIST_LEN    = 120
UID_STR_LEN       = 15
UID_STR_ADDR      = 6
CLEAR_UID_DELAY_S = 1.5
LIST1             = [1,10]
LIST2             = [11,21]
LIST3             = [22,28]
LIST              = [LIST1,LIST2,LIST3]
UID_MESSAGE_LEN   = (WHITE_LIST_LEN-2)*4


class Uid():
	def __init__(self,pos,uid):
		self.uidpos = pos
		self.uid    = uid

class WhiteList():
	def __init__(self,file_name):
		self.status         = 0
		self.uidpos         = 0
		self.uids           = []
		self.cmd            = 0
		self.len            = 0
		self.pre_delete_pos = 0
		self.delete_over    = 0
		f = open(file_name,'rU')
		self.cmds =f.readlines()
		f.close()
		self.cmdlen  = len(self.cmds)
		sel = raw_input("Please select White List : 0,1,2 \r\n>>>")
		choice = ''
		for char in sel:
				if char != ',':
					choice += char
				else:
					choice = string.atoi(choice,10)
					for i in range(LIST[choice][0],LIST[choice][1]) :
						cmd = self.cmds[i]
						cmd = cmd.strip('\n')
						cmdlen1 = len(cmd)
						j = 0
						while j < cmdlen1:
							uid = cmd[j:j+UID_STR_LEN]
							self.add(uid[UID_STR_ADDR:])
							j = j + UID_STR_LEN
					choice = ''
		print "uids count = ",self.len

	def add(self, uid):
		self.uids.append(uid)
		self.len += 1

	def delete(self, uid='', pos=WHITE_LIST_LEN):
		if uid != '':
			self.uids.remove(uid)
		if pos != WHITE_LIST_LEN:
			self.uids.remove(self.uids[pos])
		self.len -= 1

	def check(self,uid):
		for i in range(0,self.len):
			if uid == self.uids[i]:
				self.uidpos = i
				return True
		return False

	def show(self):
		print " uid sum = %3d:" % (self.len)
		str1 = ''
		i = 0
		while i < self.len :
			str1 += "[%3d]:%s" % (i,self.uids[i])
			i += 1;
			if i%5 == 0:
				print str1
				str1 = ''
			if i >= self.len:
				print str1
				str1 = ''

	def stroe(self,store_f):
		data = "len = %d:" % (self.len) , self.uids

	def clear(self):
		self.len    = 0
		self.status = 0
		self.uids   = []

	def get_update_uid_cmd(self):
		cmduids   = ''
		for uid in self.uids:
			cmduids += uid[0:8]
		#print cmduids
		return cmduids

	def xor_cmd_data(self,data):
		cmdtype   = '20'
		cmdsign   = '00000000'
		cmdlen    = "%02x" % (len(data)/2+1)
		uidlen    = "%02x" % (len(data)/8)
		i   = 0
		xor = 0
		data = cmdtype + cmdsign + cmdlen + uidlen + data
		while i < len(data):
			char  = data[i:i+2]
			i += 2
			char = string.atoi(char,16)
			xor = xor ^ char
		xor = "%02x"% xor
		cmddata = '5c' + data + xor + 'ca'
		#print cmddata
		return cmddata

	def send_data_to_stm32(self,data,send_data_f):
		cmddata = data
		cmddata = cmddata.decode("hex")
		send_data_f(cmddata)
		sleep(CLEAR_UID_DELAY_S)

	def show_message_to_user(self,send_data_f):
		print '[1].add uid '
		print '[2].delate uid '
		print '[3].clear white list '
		print '[4].show white list uids '
		print '[5].update uid to stm32'
		print '[6].check uid from stm32'
		self.cmd = input("Please input your select\r\n>>>")
		if self.cmd == 6:
			showcmd = "5C2b00000000002bCA"
			#checkcmd = checkcmd.decode("hex")
			#send_data_f(checkcmd)
			#sleep(CLEAR_UID_DELAY_S)
			self.send_data_to_stm32(showcmd,send_data_f)
			return

		if self.cmd == 5:
			# clear white list
			clearcmd = "5C22000000000022CA"
			self.send_data_to_stm32(clearcmd ,send_data_f)

			# get white list uid
			sumcmd = self.get_update_uid_cmd()

			# send data
			if len(sumcmd) > UID_MESSAGE_LEN:

				tempcmd = sumcmd[0:UID_MESSAGE_LEN]
				tempcmd = self.xor_cmd_data(tempcmd)
				self.send_data_to_stm32(tempcmd,send_data_f)

				if len(sumcmd[UID_MESSAGE_LEN:]) > UID_MESSAGE_LEN:
					tempcmd1 = sumcmd[UID_MESSAGE_LEN:]
					tempcmd2 = self.xor_cmd_data(tempcmd1[0:UID_MESSAGE_LEN])
					self.send_data_to_stm32(tempcmd2,send_data_f)

					tempcmd2 = tempcmd1[UID_MESSAGE_LEN:]
					tempcmd2 = self.xor_cmd_data(tempcmd2)
					self.send_data_to_stm32(tempcmd2,send_data_f)

				else:
					tempcmd1 = sumcmd[UID_MESSAGE_LEN:]
					tempcmd1 = self.xor_cmd_data(tempcmd1)
					self.send_data_to_stm32(tempcmd1,send_data_f)

			else:
				tempcmd = sumcmd
				tempcmd = self.xor_cmd_data(tempcmd)
				tempcmd = tempcmd.decode("hex")
				send_data_f(tempcmd)
				sleep(CLEAR_UID_DELAY_S)
			return

		if self.cmd == 4:
			self.show()
			return

		if self.cmd == 3:
			self.clear()
			clearcmd = "5C22000000000022CA"
			self.send_data_to_stm32(clearcmd ,send_data_f)
			self.show()
			return

		if self.cmd == 2:
			self.show()
			pos = ''
			delete_uids = raw_input("Please input the uid you want to delete \r\n>>>")
			#print delete_uids
			for char in delete_uids:
				if char != ',':
					pos += char
				else:
					#print pos
					pos = string.atoi(pos,10)
					if pos > self.pre_delete_pos:
						pos = pos - self.delete_over
						print  "Delete : [%3d]:%s " % (pos+self.delete_over,self.uids[pos])
						uid = self.uids[pos]
						self.pre_delete_pos = pos
						pos = ''
						self.delete(uid)
						self.delete_over += 1
					else:
						print  "Delete : [%3d]:%s " % (pos,self.uids[pos])
						uid = self.uids[pos]
						self.pre_delete_pos = pos
						pos = ''
						self.delete(uid)
						self.delete_over += 1
			self.show()
			self.delete_over    = 0
			self.pre_delete_pos = 0
			return

		if self.cmd == 1:
			self.show()
			uid = raw_input("Please input the uid you want to add \r\n>>>")
			if self.check(uid):
				print  "Fail...\r\nThe uid is in white list:[%d]:%s " % (self.uidpos,str(self.uids[self.uidpos]))
				return
			else:
				self.add(uid)
				self.show()
				return
