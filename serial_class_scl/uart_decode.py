#! /usr/bin/env python
"""\
uart_decode for serial ports.

"""
# import system module
import string

# import user module
class UartR():
	def __init__(self):
		self.status      = 0
		self.cnt         = 0
		self.xor         = 0
		self.str         = ""
		#print "UartR Class init Ok!"

	def set_status(self,x):
		self.status = x
	#	print "set_status:",status

	def get_status(self):
		return self.status

	def set_cnt(self,x):
		self.cnt = x
	#	print "set_cnt:",cnt

	def get_cnt(self):
		return self.cnt

	def cnt_dec(self):
		self.cnt = self.cnt - 1
	#	print "set_cnt:",uart_cnt

	def xor_cal(self,x):
		self.xor = self.xor ^ ord(x)
		#print "xor_cal ouput data :",hex(uart_xor)

	def set_xor(self,x):
		self.xor = x

	def get_xor(self):
		return self.xor

	def str_add(self,char):
		self.str = self.str + ' ' + char

	def str_clear(self):
		self.str = ""

	def clear_pbuf(self,x,show_f):
		if x == 0:
			show_f(self.str)
			self.str_clear()
		else:
			self.str_clear()

	def revice_status_machine(self,x,show_f,count_f):
		char = "%02x" % ord(x)
		#print char
		uart_current_status = self.get_status()

		# revice header
		if uart_current_status == 0:
			if char == "5c":
				self.str_add(char)
				self.set_status(1)
			return

		# revice cmd type
		if uart_current_status == 1:
			self.str_add(char)
			self.xor_cal(x)
			self.set_status(2)
			self.set_cnt(4)
			return

		# rvice sign id
		if uart_current_status == 2:
			self.str_add(char)
			self.xor_cal(x)
			self.cnt_dec()
			uart_current_cnt = self.get_cnt()
			if uart_current_cnt == 0:
				self.set_status(3)
			return

		# revice message data len
		if uart_current_status == 3:
			self.str_add(char)
			self.xor_cal(x)
			if ord(x) == 0:
				self.set_status(5)
				return
			self.set_status(4)
			self.set_cnt(ord(x))
			#print "message len = ",ord(x)
			return

		# revoce data
		if uart_current_status == 4:
			self.str_add(char)
			self.xor_cal(x)
			self.cnt_dec()
			uart_current_cnt = self.get_cnt()
			if uart_current_cnt == 0:
				self.set_status(5)
			return

		# revoce xor
		if uart_current_status == 5:
			uart_cal_oxr = self.get_xor()
			uart_cal_oxr = "%02x" % uart_cal_oxr
			#print "uart_revice_oxr =",char
			#print "xor_cal(x) =",uart_cal_oxr
			uart_oxr_cmp = cmp(uart_cal_oxr,char)
			#print uart_oxr_cmp
			count_f(1)
			if uart_oxr_cmp == 0:
				self.str_add(char)
				self.set_status(6)
				self.set_xor(0)
				count_f(2)
				return
			else:
				self.set_status(0)
				self.set_xor(0)
				# uart xor data err
				self.clear_pbuf(1,show_f)
				count_f(3)
				return

		# revice data end
		if uart_current_status == 6:
			if char == "ca":
				self.set_status(100)
				self.str_add(char)
				# uart xor data ok
				self.clear_pbuf(0,show_f)
				return