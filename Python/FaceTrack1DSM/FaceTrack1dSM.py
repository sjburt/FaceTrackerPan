# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 23:17:04 2013

@author: Steve
"""
import cv
import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

import PyBasicComms
import time

import PIDff

SEARCH_STEP = 2
POSMIN = 0
POSMAX = 1024
YAW_GOAL = 320
PITCH_GOAL = 240
    
    
class enumState():
    """ Possible states for state machine"""
    init = 0
    WaitLong = 1
    Acquired = 2
    LSearch  = 3
    RSearch  = 4
    WaitL = 5
    WaitR = 6
    Handshaking = 7
    
    
    def __init__(self, Type):
        self.value = Type
    def __str__(self):
        if self.value == enumState.init:
            return 'init' 
        if self.value == enumState.WaitLong:
            return 'WaitLong'
        if self.value == enumState.Acquired:
            return 'Acquired'
        if self.value == enumState.LSearch:
            return 'Lsearch' 
        if self.value == enumState.RSearch:
            return 'Rsearch'
        if self.value == enumState.WaitL:
            return 'WaitL'
        if self.value == enumState.WaitR:
            return 'WaitL'
        if self.value == enumState.Handshaking:
            return 'Handshaking'
    def __eq__(self,y):
        return self.value==y.value     

class enumEvent():
    none = 0
    doHandshake = 1
    Acquired = 2
    TimerDone = 3
    LostLeft = 4
    LostRight = 5
    AtLExtent= 6
    AtRExtent=7
    Handshook=8
    
    def __init__(self, Type):
        self.value = Type
        
    def __str__(self):
        if self.value == enumEvent.none:
            return 'none'
        if self.value == enumEvent.doHandshake:
            return 'doHandshake'
        if self.value == enumEvent.TimerDone:
            return 'timerDone'
        if self.value == enumEvent.LostLeft:
            return 'lostLeft'
        if self.value == enumEvent.LostRight:
            return 'lostRight'
        if self.value == enumEvent.AtLExtent:
            return 'atLExtent'
        if self.value == enumEvent.AtRExtent:
            return 'atRExtent'
        if self.value == enumEvent.Handshook:
            return 'Handshook'
    def __eq__(self,y):
        return self.value==y.value  



class Servo:
    def __init__(self):    
        ## todo
        try:        
            from serial.serialutil import SerialException
            self.p = PyBasicComms.PyBasicComms("COM3")
        except (SerialException):
            print "Com3 not working"
            
            q = raw_input("asdfaf")            
            
        self.pos =512 
        time.sleep(.1)

        
    def handshake(self):
        self.p.handshake()

    def setpos(self,pos):
        if pos > 1024:
            pos = 1024
        if pos < 0:
            pos = 0
        
        self.pos = pos
        self.p.setyaw(pos) 
            

    
class stateMachine:
    

    def __init__(self):
       
        self.servo=Servo()
        self.state = enumState(enumState.init)
        self.control = PIDff.PIDff(.05,.01,.01)
        self.control.setPoint(0)
        self.lastxerr = 0;
        self.pos = 512;
        self.timer = (False,0)
        self.servo.handshake()

    def handleEvent(self, event):
        if self.state == enumState(enumState.init):
                return enumState(enumState.WaitLong)
                
        if self.state == enumState(enumState.WaitLong):
            if event == enumEvent(enumEvent.Acquired):
                return enumState(enumState.Acquired)
            if event == enumEvent(enumEvent.TimerDone):
                return enumState(enumState.LSearch)
                
        if self.state == enumState(enumState.Acquired):
            if event == enumEvent(enumEvent.LostLeft):
                return enumState(enumState.WaitL)
            if event == enumEvent(enumEvent.LostRight):
                return enumState(enumState.WaitR)
        
        if self.state == enumState(enumState.LSearch):
            if event == enumEvent(enumEvent.Acquired):
                return enumState(enumState.Acquired)
            if event == enumEvent(enumEvent.AtLExtent):
                return enumState(enumState.RSearch)
                    
        if self.state == enumState(enumState.RSearch):
            if event == enumEvent(enumEvent.Acquired):
                return enumState(enumState.Acquired)
            if event == enumState(enumEvent.AtRExtent):
                return enumState(enumState.LSearch)

        if self.state == enumState(enumState.WaitL):
            if event == enumEvent(enumEvent.Acquired):
                return enumState(enumState.Acquired)
            if event == enumState(enumEvent.TimerDone):
                return enumState(enumState.LSearch)
        
        if self.state == enumState(enumState.WaitR):
            if event == enumEvent(enumEvent.Acquired):
                return enumState(enumState.Acquired)
            if event == enumEvent(enumEvent.TimerDone):
                return enumState(enumState.RSearch)
      
        return self.state


    def enterState(self,newstate):
        
        
        if newstate == enumState(enumState.WaitLong):
            self.state = enumState(enumState.WaitLong)
            self.timer = (True,time.time() + 5)
            
        if newstate == enumState(enumState.Acquired):
            self.state = enumState(enumState.Acquired)
            self.control.__init__();
            self.timer = (False,False)
        
        if newstate == enumState(enumState.LSearch):
            self.state = enumState(enumState.LSearch)
            self.timer = (False,False)
                
        if newstate == enumState(enumState.RSearch):
            self.state = enumState(enumState.RSearch)
            self.timer = (False,False)
                
        if newstate == enumState(enumState.WaitL):
            self.state = enumState(enumState.WaitL)
            self.timer = (True,time.time()+.5)

        if newstate == enumState(enumState.WaitR):
            self.state = enumState(enumState.WaitR)
            self.timer = (True,time.time()+.5)
                

    def step(self,status):
        event = enumEvent(enumEvent.none)
        
        if self.state == enumState(enumState.init):
            self.timer = (False,0)
            self.pos = 512
            event = enumEvent(enumEvent.Handshook)
            
        if self.state == enumState(enumState.WaitLong):
            print self.timer
            if status[0]:
                event = enumEvent(enumEvent.Acquired)
            elif self.timer[0] and (time.time() > self.timer[1]):
                event = enumEvent(enumEvent.TimerDone)
            elif (not self.timer[0]):
                    raise SMError("inWaitlong,but no timer")
        
        if self.state==enumState(enumState.Acquired):
            if status[0]:            
                ci = self.control.update(status[1])
                self.servo.setpos(self.pos-ci)
                print str(ci) + " " + str(self.pos)
                self.lastxerr = status[1]
            else:
                if self.lastxerr > 0:
                    event = enumEvent(enumEvent.LostLeft)
                else:
                    event = enumEvent(enumEvent.LostRight)

        if self.state==enumState(enumState.WaitL):
            if status[0]:
                event = enumEvent(enumEvent.Acquired)
            else:
                if self.timer[0] and (time.time() > self.timer[1]):
                    event = enumEvent(enumEvent.TimerDone)
                if not self.timer[0]:
                    raise StandardError
        
        if self.state==enumState(enumState.WaitR):
            if status[0]:
                event = enumEvent(enumEvent.Acquired)
            else:
                if self.timer[0] and (time.time() > self.timer[1]):
                    event = enumEvent(enumEvent.TimerDone)
                if not self.timer[0]:
                     raise StandardError    
        
        if self.state==enumState(enumState.LSearch):
            if status[0]:
                event = enumEvent(enumEvent.Acquired)
            self.pos = self.pos - SEARCH_STEP
            self.servo.setpos(self.pos)
            if self.pos < POSMIN:
                event = enumEvent(enumEvent.AtLExtent)
        
        if self.state==enumState(enumState.RSearch):
            if status[0]:
                event = enumEvent(enumEvent.Acquired)
            self.pos = self.pos + SEARCH_STEP
            self.servo.setpos(self.pos)
            if self.pos > POSMIN:
                event = enumEvent(enumEvent.AtRExtent)
            
        self.state = self.handleEvent(event)
            
        return self.state
      
      
    
class IplQImage(QtGui.QImage):
    """
    http://matthewshotton.wordpress.com/2011/03/31/python-opencv-iplimage-to-pyqt-qimage/
    A class for converting iplimages to qimages
    """
 
    def __init__(self,iplimage):
        # Rough-n-ready but it works dammit
        alpha = cv.CreateMat(iplimage.height,iplimage.width, cv.CV_8UC1)
        cv.Rectangle(alpha, (0, 0), (iplimage.width,iplimage.height), cv.ScalarAll(255) ,-1)
        rgba = cv.CreateMat(iplimage.height, iplimage.width, cv.CV_8UC4)
        cv.Set(rgba, (1, 2, 3, 4))
        cv.MixChannels([iplimage, alpha],[rgba], [
        (0, 0), # rgba[0] -> bgr[2]
        (1, 1), # rgba[1] -> bgr[1]
        (2, 2), # rgba[2] -> bgr[0]
        (3, 3)  # rgba[3] -> alpha[0]
        ])
        self.__imagedata = rgba.tostring()
        super(IplQImage,self).__init__(self.__imagedata, iplimage.width, iplimage.height, QtGui.QImage.Format_RGB32)
    
    
    
class faceWidget(QtGui.QWidget):
    
    facex = QtCore.pyqtSignal(int)    
    facey = QtCore.pyqtSignal(int)
    status= QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        self.j = stateMachine()        
        QtGui.QWidget.__init__(self)
        self._capture = cv.CreateCameraCapture(0)
        
        if not self._capture:
            print "Error opening capture device"
            sys.exit(1)
# 

        # create storage
        self.storage = cv.CreateMemStorage(128)
        self.cascade = cv.Load('haarcascade_frontalface_default.xml')

        
        
        frame = cv.QueryFrame(self._capture)
        self.setMinimumSize(frame.width,frame.height)
        self.setMaximumSize(self.minimumSize())
 

        self.image_size = cv.GetSize(frame)
 
#         create grayscale version
        self.grayscale = cv.CreateImage(self.image_size, 8, 1)
        self.smallgray = cv.CreateImage((100,75),8,1)
        
        self.xscale = frame.width/self.smallgray.width
        self.yscale = frame.height/self.smallgray.height
        self.bestface = None
        
        self._frame = None
        self.detect(frame)
        self._image = self._build_image(frame)
        # Paint every 50 ms
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.queryFrame)
        self._timer.start(100)
        

    
    def _build_image(self, frame):
        if not self._frame:
            self._frame = cv.CreateImage((frame.width, frame.height), cv.IPL_DEPTH_8U, frame.nChannels)

        if frame.origin == cv.IPL_ORIGIN_TL:
            cv.Copy(frame, self._frame)
        else:
            cv.Flip(frame, self._frame, 0)

        
        if self.faces:
            for (x,y,w,h),n in self.faces:
                cv.Rectangle(self._frame, (x*self.xscale,y*self.yscale),((x+w)*self.xscale,(y+h)*self.yscale),(128,255,128),2)
        if self.bestface:
            (x,y,w,h),n = self.bestface
            cv.Rectangle(self._frame, (x*self.xscale,y*self.yscale),((x+w)*self.xscale,(y+h)*self.yscale),(255,255,128),2)

        return IplQImage(self._frame)
 
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(QtCore.QPoint(0, 0), self._image)
 
    def queryFrame(self):
        frame = cv.QueryFrame(self._capture)
        
        self.detect(frame)
        self._image = self._build_image(frame)
        
        bestn = 0                             
        if self.faces:
            for pos,n in self.faces:
                if n > bestn:
                    self.bestface = (pos,n)
                    bestn = n
        if bestn == 0:
            self.bestface = None
            x=0
            y=0
            gotFace = False
        if self.bestface:
            pos = self.bestface[0]
            x = pos[0]*self.xscale+pos[2]*self.xscale/2 - YAW_GOAL 
            y = pos[1]*self.xscale+pos[3]*self.xscale/2 - PITCH_GOAL
            gotFace = True

        state = self.j.step((gotFace,x,y))
        
        print str(state)
        self.status.emit(str(state))
        self.facex.emit(x)
        self.facey.emit(y)
        
        
        self.update()

    def detect(self,frame):
        cv.CvtColor(frame, self.grayscale, cv.CV_RGB2GRAY)
        cv.Resize(self.grayscale,self.smallgray)

        #equalize histogram
        cv.EqualizeHist(self.smallgray, self.smallgray)
        
        # detect objects
        self.faces = cv.HaarDetectObjects(image=self.smallgray, cascade=self.cascade, storage=self.storage, scale_factor=1.2,\
                                     min_neighbors=2, flags=cv.CV_HAAR_DO_CANNY_PRUNING)
       
            



class mainwindow(QtGui.QMainWindow):
    def __init__(self):
        super(mainwindow, self).__init__()
        self.initUI()        
        
    def initUI(self):               
    
        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        vid = faceWidget(self)
        xlcd = QtGui.QLCDNumber(self)
        ylcd = QtGui.QLCDNumber(self)
        statusbox = QtGui.QLabel(self)     
        
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.StyledPanel)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(vid)
        lowerframe = QtGui.QFrame()          
        vbox.addWidget(lowerframe)
        frame.setLayout(vbox)
    
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(statusbox)        
        hbox.addWidget(xlcd)
        hbox.addWidget(ylcd)
        lowerframe.setLayout(hbox)
        
        self.setCentralWidget(frame)
        vid.facex.connect(xlcd.value)
        vid.facey.connect(ylcd.value)
        vid.status.connect(statusbox.text)

        self.setWindowTitle('1d tracker')
        
        self.show()




def main():
    app = QtGui.QApplication(sys.argv)
#    joy = Joystick()

    m = mainwindow()
    
    print "hi"
    sys.exit(app.exec_())
        
    
if __name__ ==  "__main__":
    main()