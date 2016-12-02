#! /usr/bin/env python
#coding:utf-8

__file__   = "XLiCOM.Py"
__author__ = "XIVN1987@163.com"

import sys
import ttk
import time
import serial
import threading
import Tkinter as Tk
import Tkinter as tk
import string

import uart_init
import uart_decode
import uart_message

isOpened = threading.Event()

root = Tk.Tk()
ComX = Tk.StringVar(root,'COM1')
Baud = Tk.StringVar(root,"1152000")
Dbit = Tk.StringVar(root,'8')
Sbit = Tk.StringVar(root,'1')
Chck = Tk.StringVar(root,'None')
HexD = Tk.BooleanVar(root,False)
HexO = Tk.BooleanVar(root,False)
Open = Tk.StringVar(root,u'打开串口')
availableCom = uart_init.guiscan();
SerialPort = 1
txt1 = 1

def printCoords():
    print "hello word"

def gui_show(str,mode):
    global txt1
    txt1.insert("insert",str+"\r\n")

def uart_compress_cmd_process():
    global SerialPort
    global uartr
    global uartm
    global txt1
    char = ""

    while True:
        read_char = SerialPort.read(1)
        #print read_char
        char += "%02X " % ord(read_char)
        uartr.revice_status_machine(read_char,uartm.message_show,uartm.count_inc)
        uart_current_status = uartr.get_status()
        if uart_current_status == 100:
            cmd_type = char[3:5]
            len_str  = char[18:20]
            len_int  = string.atoi(len_str, 16)
            data     = char[21:21+len_int*3]

            uartm.ReviceFunSets[cmd_type](len_int,data,gui_show)

            char = ""
            uartr.set_status(0)

def uart_send_data():
    global SerialPort
    uart_cmd_data = "5C 10 01 0C 14 55 0D 5A 00 00 00 00 00 11 03 01 01 41 53 CA C1 CA"
    uart_cmd_data = uart_cmd_data.replace(' ','')
    print uart_cmd_data
    uart_cmd_data = uart_cmd_data.decode("hex")
    SerialPort.write(uart_cmd_data)

def main():
    global txt1

    root.title("COM Shell")

    txt1 = Tk.Text(root,width=80,border=5)
    txt1.pack(side='top',padx=3,pady=1,anchor='c')

    cnv1 = tk.Canvas(root,height=26,width=580)
    cnv1.pack(side='top',padx=0,pady=0,anchor='c')
    cnv1.create_window( 30,15,window=ttk.Label(root,text=u'输入框：'))
    cnv1.create_window(210,15,window=ttk.Entry(root,width=43))
    send = ttk.Button(root,text=u'发送',width=10,command=uart_send_data)
    send.pack(side='top',padx=0,pady=0,anchor='w')
    cnv1.create_window(387,15,window=send)
    cnv1.create_window(472,15,window=ttk.Button(root,text=u'清除',width=10))
    cnv1.create_window(547,15,window=ttk.Checkbutton(root,text=u'HEX显示',variable=HexD,onvalue=True,offvalue=False))

    cnv2 = tk.Canvas(root,height=26,width=580)
    cnv2.pack(side='top',padx=0,pady=0,anchor='c')
    cnv2.create_window( 30,15,window=ttk.Label(root,text=u'串口号：'))
    cnv2.create_window(105,15,window=ttk.Combobox(root,textvariable=ComX,values=availableCom,width=12))
    cnv2.create_window(202,15,window=ttk.Label(root,text=u'波特率：'))
    cnv2.create_window(277,15,window=ttk.Combobox(root,textvariable=Baud,values=['9600','115200','1152000'],width=12))
    cnv2.create_window(398,15,window=ttk.Button(root,textvariable=Open,width=10,command=lambda:COMOpen(cnv2)))
    cnv2.create_oval(470,7,486,23,fill='black',tag='led')
    cnv2.create_window(547,15,window=ttk.Checkbutton(root,text=u'HEX发送',variable=HexO,onvalue=True,offvalue=False))

    cnv3 = tk.Canvas(root,height=26,width=580)
    cnv3.pack(side='top',padx=0,pady=0,anchor='c')
    cnv3.create_window( 30,15,window=ttk.Label(root,text=u'数据位：'))
    cnv3.create_window(105,15,window=ttk.Combobox(root,textvariable=Dbit,values=['9','8','7','6','5'],width=12))
    cnv3.create_window(202,15,window=ttk.Label(root,text=u'停止位：'))
    cnv3.create_window(277,15,window=ttk.Combobox(root,textvariable=Sbit,values=['1','2'],width=12))
    cnv3.create_window(370,15,window=ttk.Label(root,text=u'校验位：'))
    cnv3.create_window(445,15,window=ttk.Combobox(root,textvariable=Chck,values=['None','Odd','Even','Mark','Space'],width=12))
    cnv3.create_window(547,15,window=ttk.Button(root,text=u'扩展',width=9))

    cnv1.bind('<Button-1>',printCoords)

    root.mainloop()


def COMOpen(cnv2):
    global SerialPort

    if not isOpened.isSet():
        try:
            SerialPort = serial.Serial( 5, 1152000 )
        except Exception:
            print "Serial Open Error!"
        else:
            isOpened.set()
            Open.set(u'关闭串口')
            cnv2.itemconfig('led',fill='green')
            reader  = threading.Thread(target=uart_compress_cmd_process)
            print 'Process reader is going to start...'
            reader.start()
    else:
        SerialPort.close()
        isOpened.clear()
        Open.set(u'打开串口')
        cnv2.itemconfig('led',fill='black')


if __name__=='__main__':
    uartr = uart_decode.UartR()
    uartm = uart_message.UartM()
    isOpened.clear()
    main()