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

class PID:
    
	def __init__(self, P=2.0, I=0.0, D=1.0, Derivator=0, Integrator=0, Integrator_max=500, Integrator_min=-500):

		self.Kp=P
		self.Ki=I
		self.Kd=D
		self.Derivator=Derivator
		self.Integrator=Integrator
		self.Integrator_max=Integrator_max
		self.Integrator_min=Integrator_min

		self.set_point=0.0
		self.error=0.0

	def update(self,current_value):
		"""
		Calculate PID output value for given reference input and feedback
		"""

		self.error = self.set_point - current_value

		self.P_value = self.Kp * self.error
		self.D_value = self.Kd * ( self.error - self.Derivator)
		self.Derivator = self.error

		self.Integrator = self.Integrator + self.error

		if self.Integrator > self.Integrator_max:
			self.Integrator = self.Integrator_max
		elif self.Integrator < self.Integrator_min:
			self.Integrator = self.Integrator_min

		self.I_value = self.Integrator * self.Ki

		PID = self.P_value + self.I_value + self.D_value

		return PID

	def setPoint(self,set_point):
		"""
		Initilize the setpoint of PID
		"""
		self.set_point = set_point
		self.Integrator=0
		self.Derivator=0

	def setIntegrator(self, Integrator):
		self.Integrator = Integrator

	def setDerivator(self, Derivator):
		self.Derivator = Derivator

	def setKp(self,P):
		self.Kp=P

	def setKi(self,I):
		self.Ki=I

	def setKd(self,D):
		self.Kd=D

	def getPoint(self):
		return self.set_point

	def getError(self):
		return self.error

	def getIntegrator(self):
		return self.Integrator

	def getDerivator(self):
		return self.Derivator


class Servo:
    def __init__(self):    
        ## todo
        try:        
            from serial.serialutil import SerialException
            self.p = PyBasicComms.PyBasicComms("COM3")
        except (SerialException):
            print "Com3 not working"
            sys.exit(-1)
        self.setpos(512)
        time.sleep(.1)
        self.control = PID(.1,0.01,0.1)
        self.control.setPoint(320)
        
    def handshake(self):
        self.p.handshake()

    def setpos(self,pos):
        if pos > 1024:
            pos = 1024
        if pos < 0:
            pos = 0
        
        
        self.pos = pos
        self.p.seti(pos) 
            
    def scnloc(self,loc):
         ci = self.control.update(loc)
         
         self.setpos(self.pos-ci)
         print str(ci) + " " + str(self.pos)
    
    
    
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
    
    def __init__(self, parent=None):
        
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
        self.update()

    def detect(self,frame):
        cv.CvtColor(frame, self.grayscale, cv.CV_RGB2GRAY)
        cv.Resize(self.grayscale,self.smallgray)

        #equalize histogram
        cv.EqualizeHist(self.smallgray, self.smallgray)
        
        # detect objects
        self.faces = cv.HaarDetectObjects(image=self.smallgray, cascade=self.cascade, storage=self.storage, scale_factor=1.2,\
                                     min_neighbors=2, flags=cv.CV_HAAR_DO_CANNY_PRUNING)
        bestn = 0                             
        if self.faces:
            for pos,n in self.faces:
                if n > bestn:
                    self.bestface = (pos,n)
                    bestn = n
        if bestn == 0:
            self.bestface = None
        if self.bestface:
            pos = self.bestface[0]
            self.facex.emit(pos[0]*self.xscale+pos[3]*self.xscale/2)
            



class mainwindow(QtGui.QMainWindow):
    def __init__(self):
        super(mainwindow, self).__init__()

        self.j = Servo()        
        
        self.initUI()        
        
    def initUI(self):               
        
        self.j.handshake()
        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        vid = faceWidget(self)
        lcd = QtGui.QLCDNumber(self)

        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.StyledPanel)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(vid)        
        vbox.addWidget(lcd)

        frame.setLayout(vbox)
            
        self.setCentralWidget(frame)

        vid.facex.connect(lcd.display)
        self.connect(vid,QtCore.SIGNAL('facex(int)'),self.j.scnloc)

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