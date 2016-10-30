#! /usr/bin/env python
"""\
Scan for serial ports.

Part of pySerial (http://pyserial.sf.net)
(C) 2002-2003 <cliechti@gmx.net>

The scan function of this module tries to open each port number
from 0 to 255 and it builds a list of those ports where this was
successful.
"""
# import uinttest module
import unittest

# import user module
import uart_decode

class UnitTestDemo(unittest.TestCase):
	def setUp(self):
		pass
	def tearDown(self):
		pass
	def runTest(self):
		print "OK"
		
if __name__ == '__main__':
	demo = UnitTestDemo()
	demo.run()

