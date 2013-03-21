# -*- coding: utf-8 -*-
"""
Statelib
Created on Fri Mar 08 21:57:36 2013

@author: Steve

"""
import time
import inspect
from PyQt4 import QtCore

class State(QtCore.QObject):
    def __init__(self, container):
        self.container = container

        
    def handleEvent(self,  event):
        print "Error, handleEvent must be overridden in ",  type(self)
        raise RuntimeError
        
    def onStep(self):
        pass
    
    def onEnter(self):
        pass
        
    def getName(self): 
       return self.__class__.__name__
       
       

class States(QtCore.QObject):
    _states={}
    parent=None
    def __init__(self):
        super(States, self).__init__()
        for (name, aclass) in inspect.getmembers(self,  predicate = inspect.isclass):
            if issubclass(aclass, State):
                self.addState(aclass)
    
    def addState(self, newstate):
        a = newstate(self)
        self._states[a.getName()] =  a
        return a
    
    def getState(self, name):
        return self._states[name]
        
    def registerParent(self, parent):
        self.parent = parent

class Event(QtCore.QObject):
    def __init__(self, container):
        self.container = container
    def getName(self): 
       return self.__class__.__name__
       
       
        
class Events(QtCore.QObject):
    _events={}
    def __init__(self):
        super(Events, self).__init__()
        for (name, aclass) in inspect.getmembers(self,  predicate = inspect.isclass):
            if issubclass(aclass, Event):
                self.addEvent(aclass)
    def addEvent(self, newevent):
        a=newevent(self)
        self._events[a.getName()] = a
        return a
    def getEvent(self, name):
        return self._events[name]
    

def main():
    class State1(State):
        
        def onStep(self):
            print "inited"
            return EndInit
        def handleEvent(self, event):
            
            if event is EndInit:
                return self.container.getState['State2']
            else:
                return None
        
    class State2(State):
        def onEnter(self):
            self.timeToStop = time.time()+5
            print "Entered state 2"
        
        def onStep(self):
            print "state 2"
            if time.time() > self.timeToStop:
                return TimerDone
            return None
        
        def handleEvent(self, event):
            if event is TimerDone:
                return self.container.getState('Halt')
            
    
    
    class Halt(State):
        def onEnter(self):
            print "halt, finished"

    class EndInit(Event):
        pass
    class TimerDone(Event):
        pass



    s = States()

    currentState = s.addState(State1)
    s.addState(State2)
    s.addState(Halt)
    
    
    while currentState is not s.getState['Halt']:
        event = currentState.onStep()
        if event is not None:
            newState = currentState.handleEvent(event)
            if newState is not None:
                newState.onEnter()
                currentState = newState
        time.sleep(1)
    
    
if __name__ == "__main__":
    main()
else:
    print "hi"
