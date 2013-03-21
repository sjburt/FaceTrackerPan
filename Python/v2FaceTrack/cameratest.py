""" 

Cameratest.py

@Author: Steve

Software to test the camera frame rate in QT




"""
from PyQt4 import QtCore, QtGui
import cv2.cv as cv
import cv2
import sys
import time

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
        
    
class camWidget(QtGui.QWidget):
    gotFrame = QtCore.pyqtSignal()
    frametime = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(camWidget, self).__init__()

        self._capture = cv2.VideoCapture(0)
 

#        except:
#            print 'error opening camera: ' , sys.exc_info()[0]
#            
#            raise
        
        
        self.time = time.time()
        ret, imagearray = self._capture.read()
        frame=cv.fromarray(imagearray)
        self.setMinimumSize(frame.width,frame.height)
        self.setMaximumSize(self.minimumSize())

        self.image_size = cv.GetSize(frame)
    
        self._image = IplQImage(frame)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.getFrame)
        self.time = time.time()
        self._timer.start(1)
      #  QtCore.QTimer.singleShot(50, self.getFrame)
        
    def getFrame(self):
        ret, imagearray= self._capture.read()
 #       frame = cv.fromarray(imagearray)
 #       self._image = IplQImage(self._frame)
  #      self._image = QtGui.QImage(imagearray.tostring(), frame.width, frame.height, QtGui.QImage.Format_RGB888).rgbSwapped()
        self._image = QtGui.QImage(imagearray.tostring(), imagearray.shape[1], imagearray.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        self.frametime.emit(str(1/(time.time() -self.time) ) )
        self.time = time.time()
        self.update()
      
        self.gotFrame.emit()

        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(QtCore.QPoint(0, 0), self._image)
        
    def closeCap(self):
        print ('closing:', self) 
        self._capture.release()
      
      
class mainwindow(QtGui.QMainWindow):
    def __init__(self):
        
        
        super(mainwindow, self).__init__()
        self.initUI() 
        
    def initUI(self):               
        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        
        
        cam = camWidget(self)
        
        lcd = QtGui.QLabel(self)
        
        cam.frametime.connect(lcd.setText)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(cam)
        vbox.addWidget(lcd)
        
        
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.StyledPanel)
        frame.setLayout(vbox)
        
        self.setCentralWidget(frame)
        
        exitAction.triggered.connect(cam.closeCap)
       # cam.gotFrame.connect(cam.getFrame)
        self.show()
        

    


def main():
    app = QtGui.QApplication(sys.argv)

    m = mainwindow()
    

    app.exec_()
      
    
    
    
if __name__ ==  "__main__":
    main()
