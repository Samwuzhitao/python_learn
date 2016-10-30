#! /usr/bin/env python
#coding:utf-8
"""\
uart_whitelist for serial ports.

"""
import string
import sys
import os

WHITE_LIST_LEN = 120

class Uid():
	def __init__(self,pos,uid):
		self.uidpos = pos
		self.uid = uid

class WhiteList():
	def __init__(self,file_name):
		self.status = 0
		self.uidpos = 0
		self.uids   = []
		self.cmd    = 0
		self.len    = 0
		f = open(file_name,'rU')
		self.cmds =f.readlines()
		f.close()
		self.cmdlen  = len(self.cmds)
		for i in range(1,self.cmdlen) :
			cmd = self.cmds[i]
			cmd = cmd.strip('\n')
			cmdlen1 = len(cmd)
			j = 0
			while j < cmdlen1:
				uid = cmd[j:j+15]
				self.add(uid[6:])
				j = j + 15
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
		print " len = %d:" % (self.len) 
		str1 = ' '
		i = 0 
		while i < self.len :
			str1 += "[%3d]:%s, " % (i,self.uids[i])
			i += 1;
			if i%5 == 0:
				print str1
				str1 = ' '
			if i >= self.len:
				print str1

	def stroe(self,store_f):
		data = "len = %d:" % (self.len) , self.uids

	def clear(self):
		self.len    = 0
		self.status = 0
		self.uids   = []

	def get_update_uid_cmd(self):
		updatecmdheader = '5C'
		updatecmdtype   = '20'
		updatecmdsign   = '00000000'
		updatecmdlen    = "%02x" % (self.len) 
		updatecmduids   = ''
		for uid in self.uids: 
			updatecmduids += uid[0:8]
		data = updatecmdtype+updatecmdsign+updatecmdlen+updatecmduids
		#print data
		i = 0
		xor = 0
		while i < len(data):
			char = data[i:i+2]
			i += 2
			char = string.atoi(char,16)
			xor = xor ^ char
			#print char
		xor = "%02x"% xor
		cmddata = updatecmdheader + data + xor + 'ca'
		print  cmddata

	def show_message_to_user(self):
		print '[1].add uid '
		print '[2].delate uid '
		print '[3].clear white list '
		print '[4].show white list uids '
		print '[5].update uid to stm32'
		self.cmd = input("Please input your select\r\n>>>")
		if self.cmd == 5:
			self.get_update_uid_cmd()

		if self.cmd == 4:
			self.show()
			return

		if self.cmd == 3:
			self.clear()
			self.show()

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
					print  "Delete : [%3d]:%s " % (pos,self.uids[pos])
					uid = self.uids[pos]
					pos = ''
					self.delete(uid)
			self.show()

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

if __name__=='__main__':
	path = os.path.abspath("../")
	path = path + '\\Config\\' + 'white_list.txt'

	wl = WhiteList(path)

	while True:
		wl.show_message_to_user()

