# -*- coding: utf-8 -*-
"""
Created on Fri Mar 01 19:14:32 2013

@author: Steve
"""

import time
import PyBasicComms
import PIDff
import threading
from PyQt4 import QtCore


YAW_MIN = 50
YAW_MAX = 1000
YAW_DEF = 512
PITCH_MAX = 550
PITCH_MIN = 250
PITCH_DEF = 350

SEARCH_STEP =15

class StateEnum():
    """ _Vals='no_change','Init','WaitLong','Acquired','WaitL','WaitR','ScanL','ScanR']"""
    _vals=['no_change','Init','WaitLong','Acquired','WaitL','WaitR','ScanL','ScanR']
    def __init__(self,val):
        if self._vals.__contains__(val):
            self.val = val
        else:
            raise ValueError
    
    def set_val(self,val):
        if self._vals.__contains__(val):
            self.val = val
        else:
            raise ValueError
    def get_val(self,val):
        return self.val
        
    def __str__(self):
        return self.val
 
    def __eq__(self,y):
        return self.val == y


class EventEnum():
    """  _Vals=['none','done_init','DoneTimer','Acquired','LostL','LostR','AtLExtent','AtRExtent']"""
    _vals=['none','done_init','DoneTimer','Acquired','LostL','LostR','AtLExtent','AtRExtent']
    def __init__(self,val):
        if self._vals.__contains__(val):
            self.val = val
        else:
            raise ValueError
    
    def set_val(self,val):
        if self._vals.__contains__(val):
            self.val = val
        else:
            raise ValueError
    def get_val(self,val):
        return self.val
        
    def __str__(self):
        return self.val
    
    def __eq__(self,y):
        return self.val == y
 
class Servo:
    def __init__(self):    
        ## todo
        try:        
            from serial.serialutil import SerialException
            self.p = PyBasicComms.PyBasicComms("/dev/tty.usbmodemfd121")
        except (SerialException):
            print "Couldn't open port not working"
          
            
        self.yaw =YAW_DEF 
        self.pitch=PITCH_DEF
        
        
    def handshake(self):
        self.p.handshake()

    def setyaw(self,pos):
        if pos > YAW_MAX:
            pos = YAW_MAX
        if pos < YAW_MIN:
            pos = YAW_MIN
        self.yaw = pos
        self.p.setyaw(pos) 
        

    def setpitch(self,pos):
        if pos > PITCH_MAX:
            pos = PITCH_MAX
        if pos < PITCH_MIN:
            pos = PITCH_MIN
        self.pitch = pos
        self.p.setpitch(pos) 
        



class stateMachine(QtCore.QThread):
    pitchsig= QtCore.pyqtSignal(int)    
    yawsig = QtCore.pyqtSignal(int)
    status =  QtCore.pyqtSignal(str)
    def __init__(self,runSM,handshakedone):
        QtCore.QThread.__init__(self)
        self.servo = Servo();
        self.pidx = PIDff.PIDff(.11,.01,.001,6,1)
        self.pidy = PIDff.PIDff(.11,.01,.001,6,1)
        self.runSM = runSM
        self.servo.handshake()
        handshakedone.set()
        self.yaw = 512
        self.pitch = 400
        self.errx = 0;
        self.erry = 0;
        self.errx_last = 0;
        self.erry_last = 0;
        self.hasFace = False
        self.servo.setyaw(self.yaw)
        self.servo.setpitch(self.pitch)

        self.state = StateEnum('Init')
        
    def run(self):
        self.runSM.wait()
        cx=0
        cy=0
        while(self.runSM.isSet()):
            
            if self.state == StateEnum('Init'):
                event = EventEnum('done_init')
            elif self.state == StateEnum('WaitLong'):
                if self.hasFace:
                    event = EventEnum('Acquired')
                if self.timer[0]:
                    if self.timer[1] < time.time():
                        event=EventEnum('DoneTimer')
                else:
                    RuntimeError
            elif self.state == StateEnum('Acquired'):
                if self.hasFace:
                    cx = self.pidx.update(self.errx)
                    self.yaw = self.yaw - cx
                    self.servo.setyaw(self.yaw)
                    self.errx_last = self.errx
                    cy = self.pidy.update(self.erry)
                    self.pitch = self.pitch - cy
                    self.servo.setpitch(self.pitch)
                    self.erry_last = self.erry
                    
                else:
                    if self.errx_last <= 0:
                        event=EventEnum('LostL')
                    if self.errx_last > 0:
                        event=EventEnum('LostR')
            elif (self.state == StateEnum('WaitL')) or (self.state == StateEnum('WaitR')):
                self.yaw = self.yaw - cx
                self.servo.setyaw(self.yaw)
                cx=cx/2
                self.pitch = self.pitch - cy
                self.servo.setpitch(self.pitch)
                cy=cy/2
                if self.hasFace:
                    event = EventEnum('Acquired')
                if self.timer[0]:
                    if self.timer[1] < time.time():
                        event=EventEnum('DoneTimer')
                else:
                    RuntimeError
            elif self.state == StateEnum('ScanL'):
                if self.hasFace:
                    event = EventEnum('Acquired')
                else:
                    self.yaw = self.yaw -SEARCH_STEP
                    self.servo.setyaw(self.yaw)
                    self.servo.setpitch(self.pitch)
                    if self.yaw < YAW_MIN:
                        event = EventEnum('AtLExtent')
            elif self.state == StateEnum('ScanR'):
                if self.hasFace:
                    event = EventEnum('Acquired')
                else:
                    self.yaw = self.yaw + SEARCH_STEP;
                    self.servo.setyaw(self.yaw)
                    self.servo.setpitch(self.pitch)
                    if self.yaw > YAW_MAX:
                        event = EventEnum('AtRExtent')
            else:
                event = EventEnum('none')
        
            newstate=self.handleEvent(event)

            if newstate != StateEnum('no_change'):               
               self.state = self.enterState(newstate)
            event = EventEnum('none')
            self.pitchsig.emit(self.pitch)
            self.yawsig.emit(self.yaw)   
            self.status.emit(str(self.state))
            time.sleep(.05)
        
    def handleEvent(self,event):
        """Takes event and returns what state should be switched too """
        if event == EventEnum('done_init'):
            if self.state == StateEnum('Init'):
                return StateEnum('WaitLong')
            else:
                raise StandardError
        elif event == EventEnum('Acquired'):
            if self.state == StateEnum('Init'):
                return self.state
            else:
                return StateEnum('Acquired')
        elif event == EventEnum('DoneTimer'):
            if self.state == StateEnum('WaitLong'):
                return StateEnum('ScanL')
            elif self.state == StateEnum('WaitL'):
                return StateEnum('ScanL')
            elif self.state == StateEnum('WaitR'):
                return StateEnum('ScanR')
            else:
                raise StandardError
        
        elif event == EventEnum('LostL'):
            if self.state == StateEnum('Acquired'):
                return StateEnum('WaitL')
            else:
                raise StandardError
        
        elif event == EventEnum('LostR'):
            if self.state == StateEnum('Acquired'):
                return StateEnum('WaitR')
            else:
                raise StandardError
        
        elif event == EventEnum('AtLExtent'):
            if self.state == StateEnum('ScanL'):
                return StateEnum('ScanR')
            else:
                raise StandardError
        
        elif event == EventEnum('AtRExtent'):
            if self.state == StateEnum('ScanR'):
                return StateEnum('ScanL')
            else:
                raise StandardError
                
        
        else:
            return StateEnum('no_change')
        
        
        
    def enterState(self,state):
        """ Does startup tasks for each state"""
        
        if state != self.state:
            if state == StateEnum('WaitLong'):
                self.timer=(True,time.time()+5)
                return state
            elif state == StateEnum('Acquired'):
                
                self.timer=(False,0)
                return state
            elif state == StateEnum('WaitL'):
                self.timer=(True,time.time()+1)
                return state
            elif state == StateEnum('WaitR'):
                self.timer=(True,time.time()+1)
                return state            
            elif state == StateEnum('ScanL'):
                self.timer=(False,0)
                self.pidx.reset()
                self.pidy.reset()
                self.pitch=PITCH_DEF
                return state    
            elif state == StateEnum('ScanR'):
                self.timer=(False,0)
                self.pidx.reset()
                self.pidy.reset()
                self.pitch=PITCH_DEF
                return state                        
            return self.state  # do not switch state
    
    def setStatus(self,acq,errx,erry):
        self.hasFace = acq
        self.errx = errx
        self.erry = erry

    def setXerr(self,errx):
        self.errx = errx    
    def setYerr(self,erry):
        self.erry = erry
        
    def setHasFace(self,hasFace):
        self.hasFace=hasFace

    def getState(self):
        return self.state
    def getPitch(self):
        return self.pitch
    def getYaw(self):
        return self.yaw
    
        

        
                    
            
            
            
            
            

