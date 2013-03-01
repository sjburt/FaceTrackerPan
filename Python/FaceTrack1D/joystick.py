# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 23:17:04 2013

@author: Steve
"""
import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

import PyBasicComms
import time


class Joystick:
    def __init__(self):    
        ## todo
        try:        
            from serial.serialutil import SerialException
            self.p = PyBasicComms.PyBasicComms("COM3")
        except (SerialException):
            print "Com3 not working"
            sys.exit(-1)
        self.p.seti(512)
        time.sleep(.1)
        
    def handshake(self):
        self.p.handshake()

    def newpos(self,pos):
        self.p.seti(pos)    
    
        
class mainwindow(QtGui.QWidget):
    def __init__(self):
        super(mainwindow, self).__init__()

        self.j = Joystick()        
        
        self.initUI()        
        
    def initUI(self):               
        
        self.j.handshake()
        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        lcd = QtGui.QLCDNumber(self)
        sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        sld.setRange(0,1024)
 
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(lcd)
        vbox.addWidget(sld)

        self.setLayout(vbox)
        sld.valueChanged.connect(lcd.display)
        self.connect(sld,QtCore.SIGNAL('valueChanged(int)'),self.j.newpos)
        self.setGeometry(300, 300, 250, 150)
        sld.setValue(512)
        self.setWindowTitle('Joystick')
        

        self.show()

def main():
    app = QtGui.QApplication(sys.argv)
#    joy = Joystick()

    m = mainwindow()
    
    
    sys.exit(app.exec_())
        
    
if __name__ ==  "__main__":
    main()