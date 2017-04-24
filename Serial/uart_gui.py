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
import time
import threading

ser            = 0
show_time_flag = 0
inputcount     = 0
messages       = []
send_message   = ""
atuo_send_time = 0
auto_send_flag = 0

def uart_autosend_process():
    global ser
    global show_time_flag
    global inputcount
    global messages
    global send_message

    while True:
        sleep(atuo_send_time/1000)
        if ser.isOpen() == True:
            if atuo_send_time != 0:
                inputcount = inputcount + 1
                ser.write(send_message)
                data = u"<b>S[%d]:</b>%s" % (inputcount-1, send_message)
                messages.append(data)

def uart_listen_process():
    global ser
    global show_time_flag
    global inputcount
    global messages

    json_revice = json_decode()
    str_len = 0
    ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'
    
    while True:
        if ser.isOpen() == True:
            read_char = ser.read(1)
            #print read_char
            str1 = json_revice.r_machine(read_char)
            if len(str1) == 0:
                str_len = str_len + 1
            else:
                now = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
                if show_time_flag == 1:
                    data = u"【%s】 <b>R[%d]:</b>%s" % (now, inputcount-1, str1)
                else:
                    data = u"<b>R[%d]:</b>%s" % (inputcount-1, str1)
                messages.append(data)
                #print messages
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

        super(DtqDebuger, self).__init__(parent)
        inputcount = 0
        self.ports_dict = {}

        self.com_label=QLabel(u'串口：')  
        self.com_combo=QComboBox(self) 
        self.uart_scan()

        self.com_lineedit = QLineEdit(u'COM1')
        self.baudrate_label=QLabel(u"波特率：") 
        self.baudrate_lineedit = QLineEdit(u'1152000')
        self.baudrate_unit_label=QLabel(u"bps ") 

        self.displaystyle_label=QLabel(u"显示格式：")
        self.display_combo=QComboBox(self) 
        self.display_combo.addItem(u'字符串')
        self.display_combo.addItem(u'16进制')
        self.protocol_label=QLabel(u"协议版本：")
        self.protocol_combo=QComboBox(self) 
        self.protocol_combo.addItem(u'JSON')
        self.protocol_combo.addItem(u'HEX')
        self.clear_revice_button=QPushButton(u"清空数据")
        
        self.sendstyle_label=QLabel(u"发送格式：")
        self.send_combo=QComboBox(self) 
        self.send_combo.addItem(u'字符串')
        self.send_combo.addItem(u'16进制')
        self.auto_send_label=QLabel(u"自动发送") 
        self.auto_send_chackbox = QCheckBox() 

        self.show_time_label=QLabel(u"显示时间") 
        self.show_time_chackbox = QCheckBox() 

        self.send_time_label=QLabel(u"发送周期：") 
        self.send_time_lineedit = QLineEdit(u'1000')
        self.send_time_unit_label=QLabel(u"ms ") 

        self.update_fm_button=QPushButton(u"升级程序")
        self.update_fm_label=QLabel(u"固件版本：") 
        self.update_fm_combo=QComboBox(self) 
        self.update_fm_combo.addItem(u'天喻')
        self.update_fm_combo.addItem(u'自有')

        self.send_lineedit = QLineEdit(u"{'fun': 'answer_start','time': '2017-02-15:17:41:07:137','questions': [{'type': 's','id': '1','range': 'A-D'},{'type': 'm','id': '13','range': 'A-F'},{'type': 'j','id': '24','range': ''},{'type': 'd','id': '27','range': '1-5'}]}")
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
        c_hbox.addWidget(self.protocol_label)
        c_hbox.addWidget(self.protocol_combo)

        t_hbox = QHBoxLayout()
        t_hbox.addWidget(self.show_time_label)
        t_hbox.addWidget(self.show_time_chackbox)

        t_hbox.addWidget(self.auto_send_label)
        t_hbox.addWidget(self.auto_send_chackbox)

        t_hbox.addWidget(self.send_time_label)
        t_hbox.addWidget(self.send_time_lineedit)
        t_hbox.addWidget(self.send_time_unit_label)
        t_hbox.addWidget(self.sendstyle_label)
        t_hbox.addWidget(self.send_combo)
        t_hbox.addWidget(self.update_fm_label)
        t_hbox.addWidget(self.update_fm_combo)
        t_hbox.addWidget(self.update_fm_button)

        vbox = QVBoxLayout()
        vbox.addLayout(c_hbox)
        browser = QTextBrowser()
        vbox.addWidget(browser)
        vbox.addLayout(t_hbox)
        vbox.addWidget(self.send_lineedit)
        
        self.setLayout(vbox)

        self.setGeometry(600, 600, 600, 500)
        self.send_lineedit.setFocus()
        self.send_lineedit.returnPressed.connect(self.uart_send_data)
        #self.clear_revice_button.clicked.connect(self.uart_data_clear)
        self.show_time_chackbox.stateChanged.connect(self.uart_show_time_check)
        self.auto_send_chackbox.stateChanged.connect(self.uart_auto_send_check)
        self.setWindowTitle(u"答题器调试工具")

        self.timer = QTimer()
        self.timer.timeout.connect(self.uart_update_text)
        self.timer.start(100)

    def uart_show_time_check(self):
        global show_time_flag
        if self.show_time_chackbox.isChecked():
            show_time_flag = 1
        else:
            show_time_flag = 0

    def uart_auto_send_check(self):
        global send_message   
        global atuo_send_time 
        global auto_send_flag

        if self.auto_send_chackbox.isChecked():
            #show_time_flag = 1
            atuo_send_time = string.atoi(str(self.send_time_lineedit.text()))
            send_message = str(self.send_lineedit.text())
            if auto_send_flag == 0:
                auto_sender.start()
                auto_send_flag = 1
            #print atuo_send_time
            #print send_message
        else:
            atuo_send_time = 0

    def uart_update_text(self):
        global browser
        global messages

        for m in messages:
            browser.append(m)
        messages = []

    def uart_data_clear(self):
        global browser
        global messages

        browser.clear()
        messages = []

    def uart_scan(self):
        for i in range(256):
            
            try:
                s = serial.Serial(i)
                self.com_combo.addItem(s.portstr)
                self.ports_dict[s.portstr] = i
                s.close()   # explicit close 'cause of delayed GC in java
            except serial.SerialException:
                pass

    def uart_send_data(self):
        global ser
        global inputcount
        global show_time_flag

        serial_port = str(self.com_combo.currentText())
        baud_rate   = str(self.baudrate_lineedit.text())
        ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'
        now = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )

        if inputcount == 0:
            try:
                ser = serial.Serial( self.ports_dict[serial_port], string.atoi(baud_rate, 10))
            except serial.SerialException:
                ser.close() 
                pass
            
            if ser.isOpen() == True:
                browser.append("<font color=red> Open <b>%s</b> OK!</font>" % ser.portstr )
                reader.start()

                data = str(self.send_lineedit.text())
                if show_time_flag == 1:
                    browser.append(u"【%s】 <b>S[%d]:</b>%s" %(now, inputcount, data))
                else:
                    browser.append(u"<b>S[%d]:</b>%s" %(inputcount, data))
                inputcount = inputcount + 1
                ser.write(data)
            else:
                browser.append("<font color=red> Open <b>%s</b> Error!</font>" % ser.portstr )
        else:
            if ser.isOpen() == True:
                data = str(self.send_lineedit.text())
                if show_time_flag == 1:
                    browser.append(u"【%s】 <b>S[%d]:</b>%s" %(now, inputcount, data))
                else:
                    browser.append(u"<b>S[%d]:</b>%s" %(inputcount, data))
                inputcount = inputcount + 1
                ser.write(data)
            else:
                browser.append("<font color=red> Open <b>%s</b> Error!</font>" % ser.portstr )

if __name__=='__main__':
    reader      = threading.Thread(target=uart_listen_process)
    auto_sender = threading.Thread(target=uart_autosend_process)

    app = QApplication(sys.argv)
    datdebuger = DtqDebuger()
    datdebuger.show()
    exit(app.exec_())