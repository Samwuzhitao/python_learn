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


isOpened = threading.Event()

RBuf = ''
TBuf = ''

root = Tk.Tk()
ComX = Tk.StringVar(root,'COM1')
Baud = Tk.StringVar(root,"9600")
Dbit = Tk.StringVar(root,'8')
Sbit = Tk.StringVar(root,'1')
Chck = Tk.StringVar(root,'None')
HexD = Tk.BooleanVar(root,False)
HexO = Tk.BooleanVar(root,False)
Open = Tk.StringVar(root,u'打开串口')


def main():
    root.title("COM Shell")

    txt1 = Tk.Text(root,width=80,border=5)
    txt1.pack(side='top',padx=3,pady=1,anchor='c')

    cnv1 = tk.Canvas(root,height=26,width=580)
    cnv1.pack(side='top',padx=0,pady=0,anchor='c')
    cnv1.create_window( 30,15,window=ttk.Label(root,text=u'输入框：'))
    cnv1.create_window(210,15,window=ttk.Entry(root,width=44))
    cnv1.create_window(387,15,window=ttk.Button(root,text=u'发送',width=10))
    cnv1.create_window(472,15,window=ttk.Button(root,text=u'清除',width=10))
    cnv1.create_window(547,15,window=ttk.Checkbutton(root,text=u'HEX显示',variable=HexD,onvalue=True,offvalue=False))

    cnv2 = tk.Canvas(root,height=26,width=580)
    cnv2.pack(side='top',padx=0,pady=0,anchor='c')
    cnv2.create_window( 30,15,window=ttk.Label(root,text=u'串口号：'))
    cnv2.create_window(105,15,window=ttk.Combobox(root,textvariable=ComX,values=['COM1', 'COM8', 'COM10','COM14'],width=12))
    cnv2.create_window(202,15,window=ttk.Label(root,text=u'波特率：'))
    cnv2.create_window(277,15,window=ttk.Combobox(root,textvariable=Baud,values=['4800','9600','115200'],width=12))
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

    com_thread = threading.Thread(target=COMTrce)
    com_thread.setDaemon(True)
    com_thread.start()

    root.bind("<<COMRxRdy>>",lambda e: txt1.insert("insert",RBuf))

    root.mainloop()

COM = serial.Serial()
def COMOpen(cnv2):
    if not isOpened.isSet():
        try:
            COM.timeout = 1
            COM.xonxoff = 0
            COM.port = ComX.get()
            COM.parity = Chck.get()[0]
            COM.baudrate = int(Baud.get())
            COM.bytesize = int(Dbit.get())
            COM.stopbits = int(Sbit.get())
            COM.open()
        except Exception:
            print "COM Open Error!"
        else:
            isOpened.set()
            Open.set(u'关闭串口')
            cnv2.itemconfig('led',fill='green')
    else:
        COM.close()
        isOpened.clear()
        Open.set(u'打开串口')
        cnv2.itemconfig('led',fill='black')

def COMTrce():
    while True:
        if isOpened.isSet():
            RBuf = COM.read(1)          #read one, with timout
            if RBuf:
                n = COM.inWaiting()
                if n:
                    RBuf = RBuf+COM.read(n)
                    root.event_generate("<<COMRxRdy>>")

            if len(TBuf)!=0:
                COM.write(TBuf)

            time.sleep(0.01)
        time.sleep(0.05)


if __name__=='__main__':
    isOpened.clear()
    main()