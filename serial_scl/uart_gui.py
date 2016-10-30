#! /usr/bin/env python
"""\
Scan for serial ports.

Part of pySerial (http://pyserial.sf.net)
(C) 2002-2003 <cliechti@gmx.net>

The scan function of this module tries to open each port number
from 0 to 255 and it builds a list of those ports where this was
successful.
"""
# import system module
import serial
import os
import time
import string
import linecache 
import threading
import ConfigParser
import sys
from time import sleep

# import user module
import uart_init  
import uart_decode
import uart_send
import uart_message

#import GUI
from Tkinter import *  


top=Tk()   
top.geometry('600x400')  

# scan uart port
coms = uart_init.scan()
listcom = Listbox(top)
for com in coms:
	listcom.insert(1, com[1])
listcom.pack()


start = Button(top,text='Open',command=top.quit)
quit  = Button(top,text='Exit',command=top.quit)

quit.pack()
mainloop()
