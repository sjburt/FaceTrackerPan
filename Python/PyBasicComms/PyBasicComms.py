# -*- coding: utf-8 -*-

# A basic communications with the board

import serial

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from serial.serialutil import SerialException
from serialutils import full_port_name, enumerate_serial_ports


class ListPortsDialog(QDialog):
    fullname = ""    
    def __init__(self, parent=None):
        super(ListPortsDialog, self).__init__(parent)
        self.setWindowTitle('List of serial ports')

        self.ports_list = QListWidget()
        self.tryopen_button = QPushButton('Open')
        self.connect(self.tryopen_button, SIGNAL('clicked()'),
            self.on_tryopen)
            
        layout = QVBoxLayout()
        layout.addWidget(self.ports_list)
        layout.addWidget(self.tryopen_button)
        self.setLayout(layout)
        self.fill_ports_list()


    def on_tryopen(self):
        cur_item = self.ports_list.currentItem()
        if cur_item is not None:
            self.fullname = full_port_name(str(cur_item.text()))
            try:
                ser = serial.Serial(self.fullname, 38400)
                ser.close()
                QMessageBox.information(self, 'Success',
                    'Opened %s successfully' % cur_item.text())
            except SerialException, e:
                QMessageBox.critical(self, 'Failure',
                    'Failed to open %s:\n%s' % (
                        cur_item.text(), e))
      
        
    def get_port(self):
        print "hi"
        return self.fullname

    def fill_ports_list(self):
        for portname in enumerate_serial_ports():
            self.ports_list.addItem(portname)


class mainDialog(QMainWindow):
    def __init__(self, parent=None):
        super(mainDialog,self).__init__(parent)
        self.setWindowTitle('PyBasicComms')
        
        self.selectport_button=QPushButton('Pick Port')
        self.connect(self.selectport_button, SIGNAL('clicked()'),self.on_select)
        layout = QVBoxLayout()
        layout.addWidget(self.selectport_button)
        self.setLayout(layout)
        
    def on_select(self):
        diag = ListPortsDialog()
        diag.show()
        diag.exec_()
        self.portname = diag.get_port();
        print self.portname;
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = mainDialog()
    form.show()
    app.exec_()