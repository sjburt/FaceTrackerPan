""" QThread test """


from PyQt4 import QtCore
import time
import sys





class Worker(QtCore.QObject):

    finished = QtCore.pyqtSignal()
    
    def doWork(self):
        
        print "let's get busy!"
        print "working...."
        time.sleep(4)
        print "all done!"
        self.finished.emit()
        

def main():
    app = QtCore.QCoreApplication(sys.argv)
    myWorker = Worker()
    
    myThread = QtCore.QThread()
    
    
    myThread.started.connect(myWorker.doWork)
    myThread.finished.connect(myWorker.deleteLater)
    myWorker.finished.connect(myThread.quit)
    myThread.finished.connect(app.quit)
    
    myWorker.moveToThread(myThread)
    
    myThread.start()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
    
    
