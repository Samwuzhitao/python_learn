#! /usr/bin/env python
"""\
Scan for serial ports.

Part of pySerial (http://pyserial.sf.net)
(C) 2002-2003 <cliechti@gmx.net>

The scan function of this module tries to open each port number
from 0 to 255 and it builds a list of those ports where this was
successful.
"""

# uart recice status machine variable
status      = 0
cnt         = 0
xor         = 0
str         = ""

# uart send variable
max        = 0
index      = 0
cmds       = []
TEST_MAX   = 0
test_index = 0

# uart statistical result
Count      = [
	0, # Send Cmd Count
	0, # Revice Count
	0, # recice ok Count
	0  # revice err Count
]	

#uart show message variable
cmd_file_path           = ""
statistical_result_path = ""
detailed_result_path    = ""
store_switch            = 0