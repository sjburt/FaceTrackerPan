# -*- coding: utf-8 -*-

# A basic communications with the board

import serial
import threading

class SerThread(threading.Thread):
    i = 512  
    def __init__(self):
        self.ser = serial.Serial("COM3",9600,timeout=10)
        self.ser.write('a')
        print "a"
        if self.ser.read(1)=='b':
            print "b,c"
            self.ser.write('c')
        if self.ser.read(1)=='d':
            print "handshook"
        else:
            print "handshake failed"
            raise serial.serialutil.SerialError('no handshake')
            
    def run(self,comms):
        while (1):
            data = self.ser.read(1)   
            if data[0] == "r":
               # TODO: build packet
               packet=chr(0x7F)+'p'+chr(int(self.i)>>8)+chr(self.i%256)+chr(0x7f)
               self.ser.write(packet)
               
    def updatei(self,newi):
        self.i=newi
    


class PyBasicComms:
    def __init__(self,portname):
        self.sthread=SerThread()
        self.sthread.run()
        
    def testmode(self):
        self.i = 512
        key = "f"
        while key[0] != "x":
            key = (raw_input("f / v /x > "))
            if key[0] == "f":
                self.i=self.i+20
            if key[0] == "v":
                self.i=self.i-20
            print "i="+str(self.i)
            self.sthread.updatei(self.i)
            
            
    def testgeti(self):
        return self.i
    def seti(self,i):
        self.i = i

def main():
    portname = "COM3"
    p = PyBasicComms(portname)
    p.testmode()

    
if __name__ == "__main__":
    main()
    