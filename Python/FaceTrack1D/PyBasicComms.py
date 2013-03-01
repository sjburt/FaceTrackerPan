# -*- coding: utf-8 -*-

# A basic communications with the board

import serial
import threading
import time


class SerThread(threading.Thread):
    i = 512  
    def __init__(self,flag,portname):
        threading.Thread.__init__(self)
        self.ser = serial.Serial(portname,9600,timeout=None)
        self.portname = portname
        self.flag = flag
        self.ser.flushInput()
        
    def handshake(self):
        print "waiting for boot"
        time.sleep(4)
        done = 0
        print "starting handshake"
        while not done :        
            self.ser.write('a')
            print "a" 
            self.ser.timeout=5
            ch = self.ser.read(1)
            print ch
            if ch == 'b':
                print "b,c"
                self.ser.write('c')
                done = 1
            else:
                print "?"
        if self.ser.read(1)=='d':
            print "handshook"
        else:
            print "handshake failed"
            raise serial.serialutil.SerialException("Handshake fail on "+self.portname)
        self.ser.timeout=None   
        
        
    def run(self):
        while (self.flag.isSet()):
            data = self.ser.read(1)   

            if data == "r":
               packet=bytearray(chr(0x7F)+'p'+chr((int(self.i)>>8))+chr(self.i%256)+chr(0x7f))
               self.ser.write(packet)
               
    def updatei(self,newi):
        if newi>1023:
            newi=1023
        if newi<0:
            newi=0
        
        self.i=int(newi)
    def stop(self):
        self.ser.close()
    

class PyBasicComms:
    def __init__(self,portname):
        self.flag = threading.Event()
        self.sthread=SerThread(self.flag,portname)

    def handshake(self):

        self.sthread.handshake()
        self.flag.set()
        
        self.sthread.start()
        
    def seti(self,i):
        self.i = i
        self.sthread.updatei(self.i)
    def moveCW(self):
        self.i = self.i+5
        self.sthread.updatei(self.i)
    def moveCCW(self):
        self.i = self.i -5
        self.sthread.updatei(self.i)
        
    def stop(self):
        self.flag.clear()
        self.sthread.join()
        self.sthread.stop()
    
    def __del__(self):
        self.stop()
    
    def testmode(self):
        self.handshake()
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

    

def main():
    #portname = "COM3"
    portname = "/dev/tty.usbmodemfd121"
    p = PyBasicComms(portname)
    p.testmode()

    
if __name__ == "__main__":
    main()
    