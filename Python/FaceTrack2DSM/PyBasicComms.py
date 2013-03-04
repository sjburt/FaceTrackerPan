# -*- coding: utf-8 -*-

# A basic communications with the board

import serial
import threading
import time


def dirty(clean_packet):
    
    dirty_packet = ""
    dirty_packet = dirty_packet + '\x7F'

    for i,c in enumerate(clean_packet):
        if (c == '\x7e') or (c=='\x7f'):
            dirty_packet = dirty_packet + '\x7E'
            dirty_packet = dirty_packet + chr(bytearray(c)[0] ^ 0x20)
        else:
            dirty_packet = dirty_packet + c
    
    dirty_packet = dirty_packet + '\x7F'       
    return (dirty_packet)


class SerThread(threading.Thread):

    def __init__(self,flag,portname):
        threading.Thread.__init__(self)
        self.ser = serial.Serial(portname,9600,timeout=None)
        self.portname = portname
        self.flag = flag
        self.ser.flushInput()
        self.ser.flushOutput()
        
    def handshake(self):
        self.ser.setDTR(False)
        time.sleep(.1)
        self.ser.setDTR(True)
        print "waiting for boot"
        time.sleep(2)
        self.ser.flushInput()
        done = False
        print "starting handshake"
        while not done :        
            self.ser.write('a')
            self.ser.timeout=5
            ch = self.ser.read(1)
            print ch
            if ch == 'b':
                self.ser.write('c')
                done = True
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
            if data == "p":
                packet=dirty('p'+'p'+chr((int(self.yaw)>>8))+chr(self.yaw%256))
            elif data == "o":
                packet=dirty('o'+'o'+chr((int(self.pitch)>>8))+chr(self.pitch%256))
            self.ser.write(packet)
            print packet
              
    def updateyaw(self,newyaw):
        if newyaw>1023:
            newyaw=1023
        if newyaw<0:
            newyaw=0
        self.yaw=int(newyaw)


    def updatepitch(self,newi):
        if newi>700:
            newi=700
        if newi<100:
            newi=100
        self.pitch=int(newi)
        
    def stop(self):
        self.ser.close()

class PyBasicComms:
    yaw   = 512 
    pitch = 300 
    def __init__(self,portname):
        self.flag = threading.Event()
        self.sthread=SerThread(self.flag,portname)
        self.sthread.updateyaw(self.yaw)
        self.sthread.updatepitch(self.pitch)
        self.sthread.daemon=True
    
    def handshake(self):

        self.sthread.handshake()
        self.flag.set()
        self.sthread.start()
        
    def setyaw(self,yaw):
        self.yaw = yaw
        self.sthread.updateyaw(yaw)
    def moveCW(self):
        self.yaw = self.yaw+25
        self.sthread.updateyaw(self.yaw)
    def moveCCW(self):
        self.yaw = self.yaw -25
        self.sthread.updateyaw(self.yaw)
    def setpitch(self,pitch):
        self.pitch = pitch
        self.sthread.updatepitch(self.pitch)
    def moveUp(self):
        self.pitch = self.pitch-25
        self.sthread.updatepitch(self.pitch)
    def moveDown(self):
        self.pitch = self.pitch +25
        self.sthread.updatepitch(self.pitch)
        
    def stop(self):
        self.flag.clear()
        if self.sthread.isAlive():
            self.sthread.join()
            self.sthread.stop()
    
    def __del__(self):
        self.stop()
    
    def testmode(self):
        self.handshake()
        key = "f"
        while key != "x":
            key = (raw_input("wasd/x > "))
            if key.__len__() == 0:
                key = "null"
            if key[0] == "a":
                self.moveCW()
            if key[0] == "d":
                self.moveCCW()
            if key[0] == "w":
                self.moveUp()
            if key[0] == "s":
                self.moveDown()
                
        self.flag.clear()
        self.sthread.join()   
        
    

def main():
    portname = "/dev/tty.usbmodemfa131"
    p = PyBasicComms(portname)
    p.testmode()

    
if __name__ == "__main__":
    main()
    