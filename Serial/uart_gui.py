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

#import uart_decode

ser              = 0
input_count      = 0
atuo_send_time   = 0
auto_send_flag   = 0
show_time_flag   = 0
decode_type_flag = 0
hex_decode_show_style = 1
send_message     = ""

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
        global decode_type_flag 
        global send_message

        while self.working==True: 
            if input_count > 0:
                if atuo_send_time != 0:
                    input_count = input_count + 1

                    if  decode_type_flag == 1:
                        hex_message = send_message.replace(' ','')
                        #print send_message
                        hex_message = hex_message.decode("hex")
                    ser.write(hex_message)

                    if show_time_flag == 1:
                        ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'
                        now = time.strftime( ISOTIMEFORMAT,
                            time.localtime( time.time() ) )
                        send_str = u"[%s] <b>S[%d]:</b> %s" % (now,
                            input_count-1, send_message)
                    else:
                        send_str = u"<b>S[%d]:</b> %s" % (input_count-1,send_message)
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
        hex_revice  = HexDecode()
        json_revice = JsonDecode()
        ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'

        while self.working==True: 
            if ser.isOpen() == True:
                read_char = ser.read(1)
                #print read_char
                if decode_type_flag == 0:
                    str1 = json_revice.r_machine(read_char)
                if decode_type_flag == 1:
                    str1 = hex_revice.r_machine(read_char)
                if len(str1) != 0:
                    now = time.strftime( ISOTIMEFORMAT,
                        time.localtime(time.time()))
                    if show_time_flag == 1:
                        recv_str = u"[%s] <b>R[%d]:</b>" % (now, input_count-1) + u"%s" %  str1
                    else:
                        recv_str = u"<b>R[%d]:</b>" % (input_count-1) + u"%s" % str1
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

class HexDecode():
    def __init__(self):
        self.status      = 0
        self.cnt         = 0
        self.xor         = 0
        self.str         = ""
        self.ReviceFunSets           = {
            "10":self.message_show_cmd_10,"11":self.message_show_cmd_11,
            "12":self.message_show_cmd_12,"13":self.message_show_cmd_10,
            "20":self.message_show_cmd_20,"21":self.message_show_cmd_20,
            "22":self.message_show_cmd_22,"23":self.message_show_cmd_22,
            "24":self.message_show_cmd_22,"25":self.message_show_cmd_22,
            "26":self.message_show_cmd_26,"27":self.message_show_cmd_22,
            "28":self.message_show_cmd_22,"29":self.message_show_cmd_26,
            "2A":self.message_show_cmd_22,"2b":self.message_show_cmd_2b,
            "2C":self.message_show_cmd_2c,"2d":self.message_show_cmd_22,
            "2E":self.message_show_cmd_2e,"2F":self.message_show_cmd_2f,
            "30":self.message_show_cmd_30,"31":self.message_show_cmd_31,
            "40":self.message_show_cmd_22,
            "41":self.message_show_cmd_22,"42":self.message_show_cmd_26,
            "43":self.message_show_cmd_43,
            "A0":self.message_show_cmd_22,
            "E0":self.message_show_cmd_e0,
        }

    def r_machine(self,x):
        global hex_decode_show_style
        char = "%02X" % ord(x)
        #print char
        #print "status = %d" % self.status
        if self.status == 0:
            if char == "5C":
                self.str =  char
                self.status = 1
            return ""

        if self.status == 1:
            self.str = self.str + ' ' + char
            self.xor = self.xor ^ ord(x)
            self.status = 2
            self.cnt = 4
            return ""

        if self.status == 2:
            self.str = self.str + ' ' + char
            self.xor = self.xor ^ ord(x)
            self.cnt = self.cnt - 1
            if self.cnt == 0:
                self.status = 3
            return ""

        if self.status == 3:
            self.str = self.str + ' ' + char
            self.xor = self.xor ^ ord(x)
            if ord(x) == 0:
                self.status = 5
                return ""
            self.status = 4
            self.cnt = ord(x)
            #print "message len = ",ord(x)
            return ""

        if self.status == 4:
            self.str = self.str + ' ' + char
            self.xor = self.xor ^ ord(x)
            self.cnt = self.cnt - 1
            uart_current_cnt = self.cnt
            if uart_current_cnt == 0:
                self.status = 5
            return ""

        if self.status == 5:
            uart_cal_oxr = self.xor
            uart_cal_oxr = "%02X" % uart_cal_oxr
            #print "uart_revice_oxr =",char
            #print "xor_cal(x) =",uart_cal_oxr
            uart_oxr_cmp = cmp(uart_cal_oxr,char)
            if uart_oxr_cmp == 0:
                #self.str_add(char)
                self.str = self.str + ' ' + char
                self.status = 6
                self.xor = 0
                return ""
            else:
                self.status = 0
                self.xor = 0
                return ""

        if self.status == 6:
            if char == "CA":
                self.str = self.str + ' ' + char
                self.status = 0
                self.xor = 0
                # uart xor data ok
                #print self.str
                if hex_decode_show_style == 0:
                    self.str = " " + self.str
                    return self.str
                if hex_decode_show_style == 1:
                    self.str = self.message_show(self.str)
                    #cmd_type = str[4:6]
                    #self.ReviceFunSets[cmd_type](len_int,data,self.show)
                    return self.str

    def message_show(self,str):
        str = " " + str
        cmd_type = str[4:6]
        sign_str = str[7:18]
        len_str  = str[19:21]
        len_int  = string.atoi(len_str, 16)
        #print len_int
        data     = str[22:22+len_int*3]
        xor      = str[22+len_int*3:22+len_int*3+2]
        end      = str[22+(len_int+1)*3:22+(len_int+1)*3+2]
        show_str = self.ReviceFunSets[cmd_type](len_int,data)

        return show_str

    def message_status_check(self,str):
        status = string.atoi(str, 10)
        if status == 0:
            str1 = " OK"
        else:
            str1 = " FAIL"
        return str1

    def message_status_check1(self,str):
        status = string.atoi(str, 10)
        if status == 0:
            str1 = " OK"
        else:
            str1 = " BUSY"
        return str1

    def message_process_show(self,x):
        if x == 1:
            show_str = "First Statistic:"
        if x == 2:
            show_str = "Second Statistic:"
        if x == 3:
            show_str = "Third Statistic:"
        if x == 4:
            show_str = "Fourth Statistic:"
        return show_str

    def message_show_cmd_10(self,len,str):
        #print "message_show_cmd_10"
        show_str = message_status_check1(str[0:2])
        show_str += " WL_FILTER_STATUS = "+str[3:5]
        uidlen   = string.atoi(str[6:8],16)
        show_str += " WL_LEN = %d" % uidlen
        return show_str
        #show_f(show_str,'a')
        #print str

    def message_show_cmd_11(self,len,str):
        #print "message_show_cmd_10"
        show_str = ' Message : ' + str
        return show_str
        #uartc.message_show(str)

    def message_show_cmd_12(self,len,str):
        #print "message_show_cmd_12"
        #show_f(message_status_check(str[0:2]),'a')
        show_str = message_status_check1(str[0:2])
        show_str += " WL_FILTER_STATUS = "+str[3:5]
        uidlen   = string.atoi(str[6:8],16)
        show_str += " WL_LEN = %d" % uidlen
        return show_str

    def message_show_cmd_20(self,len,str):
        #print "message_show_cmd_20"
        uidlen   = string.atoi(str[0:2],16)
        show_str = " WL_OK_COUNT = %d" % uidlen
        uidlen   = string.atoi(str[27:29],16)
        show_str += " WL_LEN = %d" % uidlen
        show_str += " WL_DETAIL = "+str[3:26]
        return show_str

    def message_show_cmd_22(self,len,str):
        #print "message_show_cmd_22:white list init "
        show_str = self.message_status_check(str[0:2])
        return show_str

    def message_show_cmd_26(self,len,str):
        #print "message_show_cmd_26"
        uid = str[3:14]
        uid = uid.replace(' ','')
        show_str  = ' uPOS:[%3d] ' % string.atoi(str[0:2], 16)
        show_str += 'uID:[' + uid + ']'  + " Student ID:" + str[15:]
        return show_str

    def message_show_cmd_2b(self,len,str):
        #print "message_show_cmd_2b"
        #print str
        global uidshowindex
        global uidshowflg
        global store_uid_switch
        global uid_table_first_write

        store_uid_switch = 1
        uidlen   = string.atoi(str[0:2],16)
        show_str = " uID SUM : %d " % uidlen
        #show_f(show_str,'a')

        if uidshowflg == 0:
            uidshowindex = 0
            uidshowflg   = 1

        i = 0
        j = 0
        show_str = " "

        while i < len :
            uid = str[(i+1)*3:(i+6)*3-1]
            uid = uid.replace(' ','')
            i = i + 5
            if uid != "":
                show_str     += "[%3d].%s " % (string.atoi(uid[0:2],16),uid[2:])
                uidshowindex = uidshowindex + 1
                j = j + 1
            if j == UID_SHOW_COL_NUM:
                j = 0
                #show_f(show_str,'a')
                #show_str = " "
                store_uid_switch = 0
                uid_table_first_write = 0
                return show_str
            if i >= len :
                #show_f(show_str,'a')
                #show_str = " "
                store_uid_switch = 0
                uid_table_first_write = 0
                return show_str

    def message_show_cmd_2c(self,len,str):
        #print "message_show_cmd_2c"
        uid       = str[0:11]
        show_str  = " ID  = "+uid.replace(' ','')
        #show_f(show_str,'a')
        sw_verion = str[12:20]
        sw_verion = sw_verion.replace(' ','')
        sw1 = string.atoi(sw_verion[0:2], 10)
        sw2 = string.atoi(sw_verion[3:4], 10)
        sw3 = string.atoi(sw_verion[5:6], 10)
        show_str  += " SW  = %d.%d%d" % (sw1,sw2,sw3)
        #show_f(show_str,'a')
        hwstr = str[21:65]
        hwstr = hwstr.replace(' ','')
        hwstr = hwstr.decode("hex")
        show_str  += " HW  = "+hwstr
        #show_f(show_str,'a')
        comstr = str[66:]
        comstr = comstr.replace(' ','')
        comstr = comstr.decode("hex")
        show_str  += " COM = "+"ZKXLTEACH"
        #print show_str
        return show_str

    def message_show_cmd_2d(self,len,str):
        #print "message_show_cmd_2d"
        i = 0
        while i < len :
            uid      = str[(i)*3:(i+4)*3-1]
            show_str = " online uid %2d : %s " % (i/4,uid)
            #show_f(show_str,'a')
            i = i + 4
        return show_str

    def message_show_cmd_2e(self,len,str):
        #print "message_show_cmd_2e"
        str = str.replace(' ','')
        show_str = " Src uid :"+str
        return show_str

    def message_show_cmd_2f(self,len,str):
        #print "message_show_cmd_2f"
        return message_status_check(str[0:2])

    def message_show_cmd_30(self,len,str):
        #print "message_show_cmd_30"
        #message_process_show(string.atoi(str[0:3], 16),show_f)
        show_str = "lost:"
        show_f(show_str,'a')
        i = 1
        j = 0
        show_str = ""
        while i < len-3 :
            uid = str[(i)*3:(i+5)*3-1]
            uid = uid.replace(' ','')
            i = i + 5
            show_str += "[%3d].%s " % (string.atoi(uid[0:2], 16),uid[2:])
            j = j + 1
            if j == 5 :
                j = 0
                show_f(show_str,'a')
                show_str = ""
            if i >= len-3 :
                show_f(show_str,'a')
                show_str = ""
        show_str = "count:%d" % (len/5)
        return show_str

    def message_show_cmd_31(self,len,str):
        #print "message_show_cmd_31"
        #message_process_show(string.atoi(str[0:3], 16),show_f)
        show_str = "Ok:"
        show_f(show_str,'a')
        i = 1
        j = 0
        show_str = ""
        while i < len - 3:
            uid = str[(i)*3:(i+5)*3-1]
            uid = uid.replace(' ','')
            i = i + 5
            show_str += "[%3d].%s " % (string.atoi(uid[0:2], 16),uid[2:])
            j = j + 1
            if j == 5 :
                j = 0
                show_f(show_str,'a')
                show_str = ""
            if i >= len-3 :
                show_f(show_str,'a')
                show_str = ""

        show_str = "count:%d" % (len/5)
        #show_f(show_str,'a')
        return show_str

    def message_show_cmd_43(self,len,str):
        #print "message_show_cmd_30"
        show_str = " Online uID:"
        show_f(show_str,'a')
        i = 0
        j = 0
        show_str = ""
        while i < len-3 :
            uid = str[(i)*3:(i+5)*3-1]
            uid = uid.replace(' ','')
            i = i + 5
            show_str += "[%3d].%s " % (string.atoi(uid[0:2], 16),uid[2:])
            j = j + 1
            if j == 5 :
                j = 0
                show_f(show_str,'a')
                show_str = ""
            if i >= len-3 :
                show_f(show_str,'a')
                show_str = ""
        show_str = "count:%d" % (len/5)
        #show_f(show_str,'a')
        return show_str

    def message_show_cmd_e0(self,len,str):
        #print "message_show_cmd_fd"
        show_str = message_status_check1(str[0:2])
        show_str += " err cmd = "+str[0:2] + " err code = "+str[3:]
        return show_str

class DtqDebuger(QDialog):
    def __init__(self, parent=None):
        global ser
        global send_message 

        super(DtqDebuger, self).__init__(parent)
        input_count = 0
        self.ports_dict = {}
        self.json_cmd_dict   = {}
        self.json_cmd_dict[u'清白名单'] = "{'fun':'clear_wl'}"
        self.json_cmd_dict[u'开启绑定'] = "{'fun':'bind_start'}"
        self.json_cmd_dict[u'停止绑定'] = "{'fun':'bind_stop'}"
        self.json_cmd_dict[u'设备信息'] = "{'fun':'get_device_info'}"
        self.json_cmd_dict[u'发送题目'] ="\
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
        self.json_cmd_dict[u'查看配置'] ="{'fun':'check_config'}"
        self.json_cmd_dict[u'设置学号'] ="\
        {\
          'fun':'set_student_id',\
          'student_id':'1234'\
        }"
        self.json_cmd_dict[u'设置信道'] ="\
        {\
          'fun': 'set_channel',\
          'tx_ch': '2',\
          'rx_ch': '6'\
        }"
        self.json_cmd_dict[u'设置功率'] ="{'fun':'set_tx_power','tx_power':'5'}"
        self.json_cmd_dict[u'下载程序'] ="{'fun':'bootloader'}"

        self.hex_cmd_dict   = {}
        self.hex_cmd_dict[u'清白名单'] = "5C 22 00 00 00 00 00 22 CA"
        self.hex_cmd_dict[u'开启绑定'] = "5C 41 00 00 00 00 01 01 41 CA"
        self.hex_cmd_dict[u'停止绑定'] = "5C 41 FF FF FF FF 01 00 40 CA"
        self.hex_cmd_dict[u'设备信息'] = "5C 2C 00 00 00 00 00 2C CA"
        self.hex_cmd_dict[u'单选题目'] = "5C 10 01 0C 14 55 0D 5A 00 00 00 00 00 11 03 01 01 7F 6D CA C1 CA"
        self.hex_cmd_dict[u'发送题目'] = "5C 28 00 00 00 00 14 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 1C CA"
        self.hex_cmd_dict[u'查看配置'] = "{'fun':'check_config'}"
        self.hex_cmd_dict[u'设置学号'] = "\
        {\
          'fun':'set_student_id',\
          'student_id':'1234'\
        }"
        self.hex_cmd_dict[u'设置信道'] = "\
        {\
          'fun': 'set_channel',\
          'tx_ch': '2',\
          'rx_ch': '6'\
        }"
        self.hex_cmd_dict[u'设置功率'] = "{'fun':'set_tx_power','tx_power':'5'}"
        self.hex_cmd_dict[u'下载程序'] = "{'fun':'bootloader'}"


        self.com_label=QLabel(u'串口：')  
        self.com_combo=QComboBox(self) 
        self.uart_scan()

        self.com_lineedit = QLineEdit(u'COM1')
        self.baudrate_label=QLabel(u"波特率：") 
        self.baudrate_lineedit = QLineEdit(u'1152000')
        self.baudrate_unit_label=QLabel(u"bps ") 

        self.displaystyle_label=QLabel(u"显示格式：")
        self.display_combo=QComboBox(self) 
        self.display_combo.addItem(u'16进制')
        self.display_combo.addItem(u'字符串')
        self.display_combo.setCurrentIndex(self.display_combo.
            findText(u'字符串'))
        self.protocol_label=QLabel(u"协议版本：")
        self.protocol_combo=QComboBox(self) 
        self.protocol_combo.addItem(u'JSON')
        self.protocol_combo.addItem(u'HEX')
        self.clear_revice_button=QPushButton(u"清空数据")
        
        self.send_cmd_combo=QComboBox(self) 
        for key in self.json_cmd_dict:
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

        self.send_lineedit = QLineEdit(self.json_cmd_dict[u'设备信息'])
        self.send_lineedit.selectAll()
        self.send_lineedit.setDragEnabled(True)
        self.send_lineedit.setMaxLength(5000)

        c_hbox = QHBoxLayout()
        c_hbox.addWidget(self.com_label)
        c_hbox.addWidget(self.com_combo)
        c_hbox.addWidget(self.baudrate_label)
        c_hbox.addWidget(self.baudrate_lineedit)
        c_hbox.addWidget(self.baudrate_unit_label)
        c_hbox.addWidget(self.protocol_label)
        c_hbox.addWidget(self.protocol_combo)
        c_hbox.addWidget(self.displaystyle_label)
        c_hbox.addWidget(self.display_combo)
        c_hbox.addWidget(self.clear_revice_button)

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
        self.protocol_combo.currentIndexChanged.connect(self.update_uart_protocol)
        self.display_combo.currentIndexChanged.connect(self.update_uart_hex_decode_show_style)
        self.setWindowTitle(u"答题器调试工具")

        self.uart_listen_thread=UartListen()
        self.connect(self.uart_listen_thread,SIGNAL('output(QString)'),
            self.uart_update_text) 
        self.uart_auto_send_thread=UartAutoSend()
        self.connect(self.uart_auto_send_thread,SIGNAL('output(QString)'),
            self.uart_update_text)

    def update_uart_hex_decode_show_style(self):
        global hex_decode_show_style
        data = unicode(self.display_combo.currentText())
        if data == u'16进制':
            hex_decode_show_style = 0
        if data == u'字符串':
            hex_decode_show_style = 1

    def update_uart_protocol(self):
        global decode_type_flag
        global send_message 

        data = unicode(self.protocol_combo.currentText())
        if data == u'JSON':
            decode_type_flag = 0
            data = unicode(self.send_cmd_combo.currentText())
            self.send_lineedit.setText(self.json_cmd_dict[data])
  
        if data == u'HEX':
            decode_type_flag = 1
            data = unicode(self.send_cmd_combo.currentText())
            self.send_lineedit.setText(self.hex_cmd_dict[data])
            send_message = str(self.send_lineedit.text())
        #print decode_type_flag

    def update_uart_cmd(self):
        global decode_type_flag
        
        data = unicode(self.send_cmd_combo.currentText())
        if decode_type_flag == 0:
            self.send_lineedit.setText(self.json_cmd_dict[data])
        if decode_type_flag == 1:
            self.send_lineedit.setText(self.hex_cmd_dict[data])

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
                cmd = self.json_cmd_dict[u'下载程序']
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
        global atuo_send_time 
        global auto_send_flag
        global send_message

        if self.auto_send_chackbox.isChecked():
            #show_time_flag = 1
            send_message = str(self.send_lineedit.text())
            atuo_send_time = string.atoi(str(self.send_time_lineedit.text()))
            if auto_send_flag == 0:
                self.uart_auto_send_thread.start()
                auto_send_flag = 1
            #print atuo_send_time
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
        global decode_type_flag

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
                   self.browser.append(u"【%s】 <b>S[%d]:</b> %s"
                    % (now, input_count,data))
                else:
                    self.browser.append(u"<b>S[%d]:</b> %s" %(input_count, data))
                input_count = input_count + 1

                if  decode_type_flag == 1:
                    data = data.replace(' ','')
                    data = data.decode("hex")
                    #print data
                ser.write(data)
            else:
                self.browser.append("<font color=red> Open <b>%s</b> \
                    Error!</font>" % ser.portstr )
        else:
            if ser.isOpen() == True:
                data = str(self.send_lineedit.text())
                if show_time_flag == 1:
                    self.browser.append(u"[%s] <b>S[%d]:</b> %s" 
                        % (now, input_count, data))
                else:
                    self.browser.append(u"<b>S[%d]:</b> %s" %(input_count, data))
                input_count = input_count + 1

                if  decode_type_flag == 1:
                    data = data.replace(' ','')
                    data = data.decode("hex")
                    #print data
                ser.write(data)
            else:
                self.browser.append("<font color=red> Open <b>%s</b> \
                    Error!</font>" % ser.portstr )

if __name__=='__main__':
    app = QApplication(sys.argv)
    datdebuger = DtqDebuger()
    datdebuger.show()
    app.exec_()