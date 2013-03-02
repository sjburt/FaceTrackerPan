# -*- coding: utf-8 -*-
"""
Created on Fri Mar 01 19:14:32 2013

@author: Steve
"""

import time
import PyBasicComms
import PIDff
import threading

YAW_MIN = 50
YAW_MAX = 1000


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
            self.p = PyBasicComms.PyBasicComms("COM3")
        except (SerialException):
            print "Com3 not working"
            
            q = raw_input("asdfaf")            
            
        self.yaw =512 
        self.pitch=400
        
        
    def handshake(self):
        self.p.handshake()

    def setyaw(self,pos):
        if pos > 1024:
            pos = 1024
        if pos < 0:
            pos = 0
        self.yaw = pos
        self.p.setyaw(pos) 

    def setpitch(self,pos):
        if pos > 1024:
            pos = 1024
        if pos < 0:
            pos = 0
        self.pitch = pos
        self.p.setpitch(pos) 




class stateMachine(threading.Thread):

    def __init__(self,runSM,handshakedone):
        threading.Thread.__init__(self)
        self.servo = Servo();
        self.pid = PIDff.PIDff(.01,.01,.01)
        self.runSM = runSM
        self.servo.handshake()
        handshakedone.set()
        self.yaw = 512
        self.pitch = 400
        self.errx = 0;
        self.erry = 0;
        self.errx_last = 0;
        self.erry_last = 0;
        self.acquired = False
        self.servo.setyaw(self.yaw)
        self.servo.setpitch(self.pitch)
        
        self.state = StateEnum('Init')

    def run(self):
        self.runSM.wait()
        
        while(self.runSM.isSet()):
            print (str(self.state),self.acquired,self.errx,self.errx_last)
            if self.state == StateEnum('Init'):
                event = EventEnum('done_init')
            elif self.state == StateEnum('WaitLong'):
                if self.acquired:
                    event = EventEnum('Acquired')
                if self.timer[0]:
                    if self.timer[1] < time.time():
                        event=EventEnum('DoneTimer')
                else:
                    RuntimeError
            elif self.state == StateEnum('Acquired'):
                if self.acquired:
                    ci = self.pid.update(self.errx)
                    self.yaw = self.yaw - ci
                    self.servo.setyaw(self.yaw)
                    self.errx_last = self.errx
                else:
                    if self.errx_last <= 0:
                        event=EventEnum('LostL')
                    if self.errx_last > 0:
                        event=EventEnum('LostR')
            elif (self.state == StateEnum('WaitL')) or (self.state == StateEnum('WaitR')):
                
                if self.acquired:
                    event = EventEnum('Acquired')
                if self.timer[0]:
                    if self.timer[1] < time.time():
                        event=EventEnum('DoneTimer')
                else:
                    RuntimeError
            elif self.state == StateEnum('ScanL'):
                if self.acquired:
                    event = EventEnum('Acquired')
                else:
                    self.yaw = self.yaw - 5
                    self.servo.setyaw(self.yaw)
                    if self.yaw < YAW_MIN:
                        event = EventEnum('AtLExtent')
            elif self.state == StateEnum('ScanR'):
                if self.acquired:
                    event = EventEnum('Acquired')
                else:
                    self.yaw = self.yaw + 5;
                    self.servo.setyaw(self.yaw)
                    if self.yaw > YAW_MAX:
                        event = EventEnum('AtRExtent')
            else:
                event = EventEnum('none')
        
            newstate=self.handleEvent(event)

            if newstate != StateEnum('no_change'):               
               self.state = self.enterState(newstate)
            event = EventEnum('none')
            time.sleep(.1)
        
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
                self.timer=(True,time.time()+.5)
                return state
            elif state == StateEnum('WaitR'):
                self.timer=(True,time.time()+.5)
                return state            
            elif state == StateEnum('ScanL'):
                self.timer=(False,0)
                self.pid.reset()
                return state    
            elif state == StateEnum('ScanR'):
                self.timer=(False,0)
                self.pid.reset()
                return state                        
            return self.state  # do not switch state
    
    def setStatus(self,acq,errx,erry):
        self.acquired = acq
        self.errx = errx
        self.erry = erry

    def getState(self):
        return self.state
    
        

        
                    
            
            
            
            
            

