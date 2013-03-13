# -*- coding: utf-8 -*-
"""
Created on Fri Mar 01 19:14:32 2013

@author: Steve
"""

import time
import PyBasicComms
import PIDff

import sys
from PyQt4 import QtCore

from StateLib import State, States,Event, Events

YAW_MIN = 50
YAW_MAX = 1000
YAW_DEF = 512
PITCH_MAX = 550
PITCH_MIN = 250
PITCH_DEF = 400

SEARCH_STEP =10


class smEvents(Events):
    class TIMER_DONE(Event):
        pass
    class ALL_DONE(Event):
        pass
    class DONE_INIT(Event):
        pass
    class STOP(Event):
        pass

        
    def __init__(self):
        super(smEvents, self).__init__()
        print self._events


class smStates(States):
    
    def __init__(self):
        super(smStates, self).__init__()
        print self._states
    

    
    class INIT(State):
        def onStep(self):
            return ev.getEvent('DONE_INIT')
        def handleEvent(self, event):
            if event is ev.getEvent('DONE_INIT'):
                return st.getState('WAIT_LONG')

    class WAIT_LONG(State):
        def onEnter(self):
            self.endTime = time.time()+20
        def onStep(self):

            if self.endTime < time.time():
                print "timer done"
                return ev.getEvent('TIMER_DONE')
            else:
                return None
        def handleEvent(self,  event):
            if event is ev.getEvent('TIMER_DONE'):
                return st.getState('HALT')
            elif event is ev.getEvent('STOP'):
                return st.getState('HALT')
            else:
                return None


# TODO: TRACKING, LEFT,RIGHT,ETC
    class TRACKING(State):
        def onEnter(self):
            pass
        def onStep(self):
            pass
        def handleEvent(self):
            pass
    class WAIT_L(State):
        def onEnter(self):
            pass
        def onStep(self):
            pass
        def handleEvent(self):
            pass
    class WAIT_R(State):
        def onEnter(self):
            pass
        def onStep(self):
            pass
        def handleEvent(self):
            pass
    class SCAN_L(State):
        def onEnter(self):
            pass
        def onStep(self):
            pass
        def handleEvent(self):
            pass
        
    class SCAN_R(State):
        def onEnter(self):
            pass
        def onStep(self):
            pass
        def handleEvent(self):
            pass
            
    class HALT(State):
        def handleEvent(self):
            return None

ev = smEvents()
st = smStates()

class fakeThread(QtCore.QThread):
    def run(self):
        super(fakeThread,self).run()
        print "ran thread"

    def exit(self,val):
        super(fakeThread,self).exit(val)
        print "got exit-",val


class StateMachine(QtCore.QObject):
    """  A state machine.  """
    
    finished=QtCore.pyqtSignal()
    
    def __init__(self):
        super(StateMachine, self).__init__()
        self.letsStop = False

    
    def main(self):
        currentState = st.getState('INIT')
        currentState.onEnter()
        while currentState is not st.getState('HALT'):

            event = self.getEvents()
            if event is None:
                event = currentState.onStep()
            if event is not None:
                newState = currentState.handleEvent(event)
            if newState is not None:
                newState.onEnter()
                currentState = newState
                
            time.sleep(.2)
            event = None
            newState = None
        self.finished.emit()
        print "finished"
       
    
    def getEvents(self):
        if self.letsStop == True:
            return ev.getEvent('STOP')
        else:    
            return None

    def youShouldStop(self, signal):
        self.letsStop=signal

def main():
    
    app = QtCore.QCoreApplication(sys.argv)
    sm = StateMachine()
    
    th = fakeThread()
    sm.moveToThread(th)
    th.started.connect(sm.main)
    
    th.start()
    
    sm.finished.connect(th.terminate)
    
    while th.isRunning():
        time.sleep(.5)
        
            
        
    th.wait()
    
    sys.exit(app.exec_())
    
    
if __name__ == "__main__":
    main()


            
