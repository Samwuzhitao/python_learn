# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 10:59:35 2017

@author: john
"""
import serial
import string
import time
import os
import sys
from time import sleep
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
from ctypes import *
from math import *

ser            = 0
input_count    = 0
atuo_send_time = 0
auto_send_flag = 0
show_time_flag = 0

class UartAutoSend(QThread): 
    def __init__(self,parent=None): 
        super(UartAutoSend,self).__init__(parent) 
        self.working=True 
        self.num=0 

    def __del__(self): 
        self.working=False 
        self.wait() 

    def run(self): 
        global ser
        global input_count
        global send_message

        while self.working==True: 
            if input_count > 0:
                if atuo_send_time != 0:
                    input_count = input_count + 1
                    ser.write(send_message)
                    if show_time_flag == 1:
                        ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'
                        now = time.strftime( ISOTIMEFORMAT,
                            time.localtime( time.time() ) )
                        send_str = u"【%s】<b>S[%d]:</b>%s" % (now,
                            input_count-1, send_message)
                    else:
                        send_str = u"<b>S[%d]:</b>%s" % (input_count-1,
                            send_message)
                    self.emit(SIGNAL('output(QString)'),send_str) 
                    sleep(atuo_send_time*1.0/1000)

class UartListen(QThread): 
    def __init__(self,parent=None): 
        super(UartListen,self).__init__(parent) 
        self.working=True 
        self.num=0 

    def __del__(self): 
        self.working=False 
        self.wait() 

    def run(self): 
        global ser
        json_revice = JsonDecode()
        ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'

        while self.working==True: 
            if ser.isOpen() == True:
                read_char = ser.read(1)
                #print read_char
                str1 = json_revice.r_machine(read_char)
                if len(str1) != 0:
                    now = time.strftime( ISOTIMEFORMAT,
                        time.localtime(time.time()))
                    if show_time_flag == 1:
                        recv_str = u"【%s】 <b>R[%d]:</b>%s" % (now, 
                            input_count-1, str1)
                    else:
                        recv_str = u"<b>R[%d]:</b>%s" % (input_count-1, str1)
                    #messages.append(data)
                    #print file_str
                    self.emit(SIGNAL('output(QString)'),recv_str) 
                    #self.sleep(3) 

class JsonDecode():
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

        super(DtqDebuger, self).__init__(parent)
        input_count = 0
        self.ports_dict = {}
        self.cmd_dict   = {}
        self.cmd_dict[u'清白名单'] = "{'fun':'clear_wl'}"
        self.cmd_dict[u'开启绑定'] = "{'fun':'bind_start'}"
        self.cmd_dict[u'停止绑定'] = "{'fun':'bind_stop'}"
        self.cmd_dict[u'设备信息'] = "{'fun':'get_device_info'}"
        self.cmd_dict[u'发送题目'] ="\
        {\
          'fun': 'answer_start',\
          'time': '2017-02-15:17:41:07:137',\
          'questions': [\
            {'type': 's','id': '1','range': 'A-D'},\
            {'type': 'm','id': '13','range': 'A-F'},\
            {'type': 'j','id': '24','range': ''},\
            {'type': 'd','id': '27','range': '1-5'\
            }\
          ]\
        }"
        self.cmd_dict[u'查看配置'] ="{'fun':'check_config'}"
        self.cmd_dict[u'设置学号'] ="\
        {\
          'fun':'set_student_id',\
          'student_id':'1234'\
        }"
        self.cmd_dict[u'设置信道'] ="\
        {\
          'fun': 'set_channel',\
          'tx_ch': '2',\
          'rx_ch': '6'\
        }"
        self.cmd_dict[u'设置功率'] ="{'fun':'set_tx_power','tx_power':'5'}"
        self.cmd_dict[u'下载程序'] ="{'fun':'bootloader'}"

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
        
        self.send_cmd_combo=QComboBox(self) 
        for key in self.cmd_dict:
            self.send_cmd_combo.addItem(key)
        self.send_cmd_combo.setCurrentIndex(self.send_cmd_combo.
            findText(u'设备信息'))

        self.auto_send_label=QLabel(u"自动发送") 
        self.auto_send_chackbox = QCheckBox() 

        self.show_time_label=QLabel(u"显示时间") 
        self.show_time_chackbox = QCheckBox() 

        self.send_time_label=QLabel(u"发送周期：") 
        self.send_time_lineedit = QLineEdit(u'4000')
        self.send_time_unit_label=QLabel(u"ms ") 

        self.update_fm_button=QPushButton(u"升级程序")

        self.send_lineedit = QLineEdit(self.cmd_dict[u'设备信息'])
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
        t_hbox.addWidget(self.update_fm_button)

        d_hbox = QHBoxLayout()
        d_hbox.addWidget(self.send_cmd_combo)
        d_hbox.addWidget(self.send_lineedit)

        self.browser = QTextBrowser()
        vbox = QVBoxLayout()
        vbox.addLayout(c_hbox)
        vbox.addWidget(self.browser)
        vbox.addLayout(t_hbox)
        vbox.addLayout(d_hbox)
        
        self.setLayout(vbox)

        self.setGeometry(600, 600, 600, 500)
        self.send_lineedit.setFocus()

        self.send_lineedit.returnPressed.connect(self.uart_send_data)
        #self.clear_revice_button.clicked.connect(self.uart_data_clear)
        self.show_time_chackbox.stateChanged.connect(self.uart_show_time_check)
        self.auto_send_chackbox.stateChanged.connect(self.uart_auto_send_check)
        self.update_fm_button.clicked.connect(self.uart_download_image)
        self.send_cmd_combo.currentIndexChanged.connect(self.update_uart_cmd)
        self.setWindowTitle(u"答题器调试工具")

        self.uart_listen_thread=UartListen()
        self.connect(self.uart_listen_thread,SIGNAL('output(QString)'),
            self.uart_update_text) 
        self.uart_auto_send_thread=UartAutoSend()
        self.connect(self.uart_auto_send_thread,SIGNAL('output(QString)'),
            self.uart_update_text)

    def update_uart_cmd(self):
        data = unicode(self.send_cmd_combo.currentText())
        self.send_lineedit.setText(self.cmd_dict[data])

    def uart_download_image(self):
        global ser
        global input_count

        data_path  = os.path.abspath("./") +'\\data\\'
        dll_path   = data_path + 'ExtraPuTTY.dll'
        image_path = data_path + 'DTQ_RP551CPU_ZKXL0200_V0102.bin'

        print dll_path
        print image_path

        if ser != 0:
            if ser.isOpen() == True:
                cmd = self.cmd_dict[u'下载程序']
                self.browser.append(u"<b>S[%d]:</b>%s" %(input_count, cmd))
                input_count = input_count + 1
                ser.write(cmd)

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
                self.uart_auto_send_thread.start()
                auto_send_flag = 1
            #print atuo_send_time
            #print send_message
        else:
            atuo_send_time = 0

    def uart_update_text(self,data):
        self.browser.append(data)

    def uart_data_clear(self):
        global messages

        self.browser.clear()
        messages = []

    def uart_scan(self):
        for i in range(256):
            
            try:
                s = serial.Serial(i)
                self.com_combo.addItem(s.portstr)
                self.ports_dict[s.portstr] = i
                s.close()
            except serial.SerialException:
                pass

    def uart_send_data(self):
        global ser
        global input_count
        global show_time_flag

        serial_port = str(self.com_combo.currentText())
        baud_rate   = str(self.baudrate_lineedit.text())
        ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'
        now = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )

        if input_count == 0:
            try:
                ser = serial.Serial( self.ports_dict[serial_port], 
                    string.atoi(baud_rate, 10))
            except serial.SerialException: 
                pass
            
            if ser.isOpen() == True:
                self.browser.append("<font color=red> Open <b>%s</b> \
                    OK!</font>" % ser.portstr )
                self.uart_listen_thread.start()

                data = str(self.send_lineedit.text())
                if show_time_flag == 1:
                   self.browser.append(u"【%s】 <b>S[%d]:</b>%s"
                    % (now, input_count,data))
                else:
                    self.browser.append(u"<b>S[%d]:</b>%s" %(input_count, data))
                input_count = input_count + 1
                ser.write(data)
            else:
                self.browser.append("<font color=red> Open <b>%s</b> \
                    Error!</font>" % ser.portstr )
        else:
            if ser.isOpen() == True:
                data = str(self.send_lineedit.text())
                if show_time_flag == 1:
                    self.browser.append(u"【%s】 <b>S[%d]:</b>%s" 
                        % (now, input_count, data))
                else:
                    self.browser.append(u"<b>S[%d]:</b>%s" %(input_count, data))
                input_count = input_count + 1
                ser.write(data)
            else:
                self.browser.append("<font color=red> Open <b>%s</b> \
                    Error!</font>" % ser.portstr )

if __name__=='__main__':
    app = QApplication(sys.argv)
    datdebuger = DtqDebuger()
    datdebuger.show()
    app.exec_()