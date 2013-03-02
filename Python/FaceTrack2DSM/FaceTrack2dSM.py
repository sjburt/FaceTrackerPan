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

import StateMachine
import threading
import time

YAW_GOAL = 320
PITCH_GOAL = 240



      
    
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
    pitch= QtCore.pyqtSignal(int)    
    yaw = QtCore.pyqtSignal(int)
    status= QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        self.runSM = threading.Event()
        self.handshakedone=threading.Event()
        self.SM = StateMachine.stateMachine(self.runSM,self.handshakedone)        
        QtGui.QWidget.__init__(self)
        self._capture = cv.CreateCameraCapture(0)
        self.time = time.time()
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
        self.smallgray = cv.CreateImage((160,120),8,1)
        
        self.xscale = frame.width/self.smallgray.width
        self.yscale = frame.height/self.smallgray.height
        self.bestface = None
        
        self._frame = None
        self.detect(frame)
        self._image = self._build_image(frame)
        # Paint every 50 ms
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.queryFrame)

        
        self.runSM.set()
        self.SM.start()
        self.handshakedone.wait()
        self._timer.start(50)
        

    
    def _build_image(self, frame):
        if not self._frame:
            self._frame = cv.CreateImage((frame.width, frame.height), cv.IPL_DEPTH_8U, frame.nChannels)

        if frame.origin == cv.IPL_ORIGIN_TL:
            cv.Copy(frame, self._frame)
        else:
            cv.Flip(frame, self._frame, 0)

        
    #    if self.faces:
       #    for (x,y,w,h),n in self.faces:
      #          cv.Rectangle(self._frame, (x*self.xscale,y*self.yscale),((x+w)*self.xscale,(y+h)*self.yscale),(128,255,128),2)
     #           cv.Circle(self._frame, (int((x+int(w/2)) * self.xscale),int((y+int(h/2)) * self.yscale)),5,(255,255,128),2)

        if self.bestface:
            (x,y,w,h),n = self.bestface
            cv.Rectangle(self._frame, (x*self.xscale,y*self.yscale),((x+w)*self.xscale,(y+h)*self.yscale),(255,255,128),2)
            cv.Circle(self._frame, (int((x+int(w/2)) * self.xscale),int((y+int(h/2)) * self.yscale)),5,(255,255,128),2)
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
        self.SM.setStatus(gotFace,x,y)
            

        state =self.SM.getState()
        
        

        self.status.emit(str(state))
        if state==StateMachine.StateEnum('Acquired'):  
            self.facex.emit(x)
            self.facey.emit(y)
       
        self.pitch.emit(self.SM.getPitch())
        self.yaw.emit(self.SM.getYaw())


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
        yawlcd=QtGui.QLCDNumber(self)
        pitchlcd=QtGui.QLCDNumber(self)
        modebox = QtGui.QLabel(self)
        
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.StyledPanel)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(vid)
        lowerframe = QtGui.QFrame()
        lowerframe2 = QtGui.QFrame()            
        vbox.addWidget(lowerframe)
        vbox.addWidget(lowerframe2)
        vbox.addWidget(modebox)
        frame.setLayout(vbox)
        
        lowerframe.setFixedHeight(100)
        lowerframe2.setFixedHeight(100)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(xlcd)
        hbox.addWidget(ylcd)

        hbox2 =QtGui.QHBoxLayout()
        hbox2.addWidget(yawlcd)
        hbox2.addWidget(pitchlcd)
        

        lowerframe.setLayout(hbox)
        lowerframe2.setLayout(hbox2)
        self.setCentralWidget(frame)
        vid.facey.connect(xlcd.display)
        vid.facey.connect(ylcd.display)
        vid.pitch.connect(pitchlcd.display)
        vid.yaw.connect(yawlcd.display)
        vid.status.connect(modebox.setText)

        


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
