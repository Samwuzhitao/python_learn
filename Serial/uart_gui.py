# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 10:59:35 2017

@author: john
"""

import sys
from time import sleep
from math import *
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
import serial
import string
import threading

ser        = 0
open_flag  = 0

inputcount = 0

def uart_listen_process():
    global ser
    global browser
    global open_flag
    global inputcount

    json_revice = json_decode()
    str_len = 0

    while True:
        if open_flag == 1:
            read_char = ser.read(1)
            #print read_char
            str1 = json_revice.r_machine(read_char)
            if len(str1) == 0:
                str_len = str_len + 1
            else:
                #print "len : %d %s" % (str_len, str)
                browser.append("<b>Output[%d]:</b>%s" % (inputcount-1, str1))
                str_len = 0

class json_decode():
    def __init__(self):
        self.status      = 0
        self.cnt         = 0
        self.str         = ""

    def r_machine(self,x):
        char = x
        #print "status = %d cnt = %d str: %s" % (self.status,self.cnt,self.str)

        # revice header
        if self.status == 0:
            self.str = ""
            if char == '{':
                self.str =  char
                self.cnt = self.cnt + 1
                self.status = 1
                return ""

        # revice data
        if self.status == 1:
            self.str = self.str + char
            if char == '{':
                self.cnt = self.cnt + 1
                return ""
            if char == '}':
                self.cnt = self.cnt - 1
                if self.cnt == 0:
                    #print self.str
                    self.status = 0
                    self.cnt    = 0
                    return self.str
                else:
                    return ""
        return ""

class DtqDebuger(QDialog):
    def __init__(self, parent=None):
        global ser
        global browser
        global open_flag

        super(DtqDebuger, self).__init__(parent)
        inputcount = 0
        self.ports_dict = {}

        self.com_label=QLabel(u'串口：')  
        self.com_combo=QComboBox(self) 
        self.uart_scan()

        self.com_lineedit = QLineEdit(u'COM1')
        self.baudrate_label=QLabel(u"波特率：") 
        self.baudrate_lineedit = QLineEdit(u'1152000')
        self.baudrate_unit_label=QLabel(u"/bps ") 

        self.displaystyle_label=QLabel(u"显示格式：")
        self.display_combo=QComboBox(self) 
        self.display_combo.addItem(u'字符串')
        self.display_combo.addItem(u'16进制')
        self.open_button=QPushButton(u"打开串口")
        self.clear_revice_button=QPushButton(u"清除接收数据")

        self.sendstyle_label=QLabel(u"发送格式：")
        self.send_combo=QComboBox(self) 
        self.send_combo.addItem(u'字符串')
        self.send_combo.addItem(u'16进制')
        self.auto_send_label=QLabel(u"自动发送") 
        self.auto_send_chackbox = QCheckBox() 
        self.send_time_label=QLabel(u"发送周期：") 
        self.send_time_lineedit = QLineEdit(u'1000')
        self.send_time_unit_label=QLabel(u"/ms ") 
        self.autosend_button=QPushButton(u"发送数据")
        self.clear_send_button=QPushButton(u"清除发送数据")

        self.send_lineedit = QLineEdit(u"{'fun': 'get_device_info'}")
        self.send_lineedit.selectAll()
        self.send_lineedit.setDragEnabled(True)
        self.send_lineedit.setMaxLength(5000)

        c_hbox = QHBoxLayout()
        c_hbox.addWidget(self.com_label)
        c_hbox.addWidget(self.com_combo)
        c_hbox.addWidget(self.baudrate_label)
        c_hbox.addWidget(self.baudrate_lineedit)
        c_hbox.addWidget(self.baudrate_unit_label)
        c_hbox.addWidget(self.displaystyle_label)
        c_hbox.addWidget(self.display_combo)
        c_hbox.addWidget(self.clear_revice_button)
        c_hbox.addWidget(self.open_button)

        t_hbox = QHBoxLayout()
        t_hbox.addWidget(self.auto_send_label)
        t_hbox.addWidget(self.auto_send_chackbox)
        t_hbox.addWidget(self.send_time_label)
        t_hbox.addWidget(self.send_time_lineedit)
        t_hbox.addWidget(self.send_time_unit_label)
        t_hbox.addWidget(self.sendstyle_label)
        t_hbox.addWidget(self.send_combo)
        t_hbox.addWidget(self.clear_send_button)
        t_hbox.addWidget(self.autosend_button)

        vbox = QVBoxLayout()
        vbox.addLayout(c_hbox)
        browser = QTextBrowser()
        vbox.addWidget(browser)
        vbox.addLayout(t_hbox)
        vbox.addWidget(self.send_lineedit)
        
        self.setLayout(vbox)

        self.setGeometry(600, 600, 600, 500)
        self.send_lineedit.setFocus()
        self.connect(self.open_button,SIGNAL('clicked()'),self.uart_open)
        self.connect(self.send_lineedit, SIGNAL("returnPressed()"), self.uart_send_data)
        self.setWindowTitle(u"答题器调试工具")

    def updateUi(self):
        global browser
        global inputcount

        try:
            text = unicode(self.lineedit.text())
            browser.append(" <b>Input[%d]:</b>%s =%s" %(inputcount, text, eval(text)))
            inputcount = inputcount + 1
        except:
            self.browser.append("<font color=red>%s is invalid!</font>" % text)

    def uart_scan(self):
        for i in range(256):
            
            try:
                s = serial.Serial(i)
                self.com_combo.addItem(s.portstr)
                self.ports_dict[s.portstr] = i
                s.close()   # explicit close 'cause of delayed GC in java
            except serial.SerialException:
                pass

    def uart_open(self):
        global ser
        global browser
        global open_flag
        global reader
        global inputcount

        if open_flag == 0:
            serial_port = str(self.com_combo.currentText())
            baud_rate   = str(self.baudrate_lineedit.text())
            ser = serial.Serial( self.ports_dict[serial_port], string.atoi(baud_rate, 10))
            open_flag = 1
            browser.append("Open %s OK!" % ser.port )
            #print 'Process reader is going to start...'
            if( inputcount == 0):
                reader.start()

            init_data = "{'fun': 'get_device_info'}"
            browser.append("<b>Input [%d]:</b>%s" %( inputcount, init_data))
            inputcount = inputcount + 1
            ser.write(init_data)
        else:
            browser.append("Close %s OK!" % ser.port )
            ser.close() 
            open_flag = 0

    def uart_send_data(self):
        global ser
        global inputcount
        global open_flag

        if open_flag == 0:
            serial_port = str(self.com_combo.currentText())
            baud_rate   = str(self.baudrate_lineedit.text())
            ser = serial.Serial( self.ports_dict[serial_port], string.atoi(baud_rate, 10))
            open_flag = 1

        if( inputcount == 0):
            reader.start()

        data = str(self.send_lineedit.text())

        browser.append("<b>Input [%d]:</b>%s" %(inputcount, data))
        inputcount = inputcount + 1
        ser.write(data)

if __name__=='__main__':
    reader = threading.Thread(target=uart_listen_process)

    app = QApplication(sys.argv)
    datdebuger = DtqDebuger()
    datdebuger.show()
    exit(app.exec_())