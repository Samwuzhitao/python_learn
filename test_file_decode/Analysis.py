#! /usr/bin/env python
#coding:utf-8
"""\
decode and statistic uart message for clickers.
date:2016-10-16
"""

import os
import string

class TestFile():
	def __init__(self,file_name):
		self.max          = 0
		self.str          = ""
		self.lineindex    = 0
		self.count        = 0
		self.ok           = [0,0,0,0]
		self.linecount    = [0,0,0,0]
		self.sumcount     = 0
		self.lostflg      = 0
		self.lostuid      = ""
		self.analysispath = ""
		f = open(file_name,'rU')
		self.filelines  = f.readlines()
		f.close()
		print "Test file name: " + file_name
		print "Test file len : ",len(self.filelines)

	def show(self,str,mode):
		print str
		f = open(self.analysispath,mode)
		print >> f, str
		f.close()

	def set_count_num(self,str1):
		if ((str1[0:1]  != "[") & (str1[2:3] == "1")):
			self.count = 1
		if ((str1[0:1]  != "[") & (str1[2:3] == "2")):
			self.count = 2
		if ((str1[0:1]  != "[") & (str1[2:3] == "3")):
			self.count = 3
		if ((str1[0:1]  != "[") & (str1[2:3] == "4")):
			self.count = 4

	def show_lost_uid(self,str1):
		if str1[0:5]  == "lost:":
			if self.count == 3:
				if self.sumcount != self.max:
					self.lostflg = 1
		if self.lostflg == 1:
			if str1[0:1]  == "[":
				for i in range(0,len(str1)/14):
					str2 = str1[i*14:14+i*14]
					self.lostuid = self.lostuid + str2[1:4] + ", "
		if str1[0:3]  == "ok:":
			if self.count == 3:
				if self.sumcount != self.max:
					self.lostflg = 0

	def result_check(self,str1,check_lineindex):
		if self.count == check_lineindex:
			self.sumcount += string.atoi(str1[6:], 10)
			self.linecount[check_lineindex-1] += string.atoi(str1[6:], 10)
			self.str = self.str + " " + "[%d]:count=" % self.count + "%3d" % self.linecount[check_lineindex-1] + ","
			if self.sumcount == self.max:
				self.ok[check_lineindex-1] = self.ok[check_lineindex-1] + 1
				self.sumcount = 0

	def get_num_of_clicker(self):
		for str in self.filelines:
			str = str.strip('\n')
			if str[0:3]  == "Sum":
				tempmax = string.atoi(str[10:])
				if tempmax > self.max:
					self.max = tempmax

	def result_analysis(self,str):
		str1 = str
		str1 = str1.strip('\n')

		self.set_count_num(str1)
		self.show_lost_uid(str1)

		if str1[0:5]  == "count":
			self.result_check(str1,1)
			self.result_check(str1,2)
			self.result_check(str1,3)
			self.result_check(str1,4)

		if str[0:3]  == "Sum":
			self.str ="<%03d>" % self.lineindex + self.str + " Sum:" + str1[10:13] +", "
			#self.str ="<%03d>" % self.lineindex
			self.lineindex = self.lineindex+1
			self.count = 0
			if self.sumcount != 0:
				show_str = self.str + "lost uid: " + self.lostuid
				tf.show(show_str,'a')
			else:
				show_str = self.str
				tf.show(show_str,'a')
			self.str        = ""
			self.lostuid    = ""
			self.sumcount   = 0
			self.linecount = [0,0,0,0]

	def decode_file(self):
		for line in self.filelines:
			self.result_analysis(line)

if __name__=='__main__':
	# get uart configuration
	path = os.path.abspath("./")

	# get the cmd num of the file 'testfile.txt'
	file_path = path + '\\testfile.txt'
	tf = TestFile(file_path)
	tf.analysispath = path + '\\analysisfile.txt'

	show_str =  "Test result analysis:"
	tf.show(show_str,'w')
	tf.get_num_of_clicker();
	show_str = "The number of clicker: %3d " % (tf.max)
	tf.show(show_str,'a')
	tf.decode_file()

	show_str = "Test statistical result:"
	tf.show(show_str,'a')
	show_str = "Sum     count : %2d" % tf.lineindex
	tf.show(show_str,'a')
	ok_count = tf.ok[0] + tf.ok[1] + tf.ok[2] + tf.ok[3]
	show_str = "Success count : %2d" % ok_count + "  < %7.3f %% >" % (ok_count*100.0 / tf.lineindex)
	tf.show(show_str,'a')
	one_ok_rate   = "  < %7.3f %% >" % (tf.ok[0]*100.0/tf.lineindex)
	show_str = "One     count : %2d" % tf.ok[0]   + one_ok_rate
	tf.show(show_str,'a')
	two_ok_rate   = "  < %7.3f %% >" % (tf.ok[1]*100.0/tf.lineindex)
	show_str = "Two     count : %2d" % tf.ok[1]   + two_ok_rate
	tf.show(show_str,'a')
	three_ok_rate = "  < %7.3f %% >" % (tf.ok[2]*100.0/tf.lineindex)
	show_str = "Three   count : %2d" % tf.ok[2] + three_ok_rate
	tf.show(show_str,'a')
	four_ok_rate  = "  < %7.3f %% >" % (tf.ok[3]*100.0/tf.lineindex)
	show_str = "Four    count : %2d" % tf.ok[3]  + four_ok_rate
	tf.show(show_str,'a')
	fail_rate     = "  < %7.3f %% >" % ((tf.lineindex - ok_count)*100.0/tf.lineindex)
	show_str = "Fail    count : %2d" % (tf.lineindex - ok_count) + fail_rate
	tf.show(show_str,'a')