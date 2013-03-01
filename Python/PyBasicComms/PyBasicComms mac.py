# -*- coding: utf-8 -*-

# A basic communications with the board

import serial
import threading
import time


class SerThread(threading.Thread):
    i = 512  
    def __init__(self,flag):
        threading.Thread.__init__(self)
        self.ser = serial.Serial("/dev/tty.usbmodemfd121",9600,timeout=None)
        self.flag = flag
        time.sleep(4)
        done = 0
        while not done :        
            self.ser.write('a')
            print "a"
            ch = self.ser.read(1)
            print ch
            if ch == 'b':
                print "b,c"
                self.ser.write('c')
                done = 1
            else:
                print "hi"
    
            
        if self.ser.read(1)=='d':
            print "handshook"
        else:
            print "handshake failed"
            raise self.ser.serialutil.SerialError('no handshake')
            
    def run(self):
        while (self.flag.isSet()):
            data = self.ser.read(1)   
            if data[0] == "r":
               # TODO: build packet
               packet=bytearray(chr(0x7F)+'p'+chr((int(self.i)>>8))+chr(self.i%256)+chr(0x7f))
               self.ser.write(packet)
               
    def updatei(self,newi):
        self.i=newi
    def stop(self):
        self.ser.close()
    

class PyBasicComms:
    def __init__(self,portname):
        self.flag = threading.Event()
        self.flag.set()
        self.sthread=SerThread(self.flag)
        self.sthread.start()
        
    def testmode(self):
        self.i = 512
        key = "f"
        while key != "x":
            key = (raw_input("f / v /x > "))
            if key.__len__() == 0:
                key = "null"
            if key[0] == "f":
                self.i=self.i+20
            if key[0] == "v":
                self.i=self.i-20
            print "i="+str(self.i)
            self.sthread.updatei(self.i)
        self.flag.clear()
        self.sthread.join()   
        self.sthread.stop()
        
    def testgeti(self):
        return self.i
    def seti(self,i):
        self.i = i
    def moveCW(self):
        self.i = self.i+20
    def moveCCW(self):
        self.i = self.i -20
    

def main():
    portname = "COM3"
    p = PyBasicComms(portname)
    p.testmode()

    
if __name__ == "__main__":
    main()
    