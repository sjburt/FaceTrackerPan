# -*- coding: utf-8 -*-
"""
Statelib
Created on Fri Mar 08 21:57:36 2013

@author: Steve

"""



class State():
    """ Base class for state.
    Must override  handleEvent. 
    Can optionally override enterState and onStep """
    
    def __init__(self):
        pass
        
    def onEnter(self, context):
        pass
    
    def handleEvent(self,event, context):
        print "Error: event handler not overridden for state ", self.__name
        raise TypeError
        
    def onStep(self, context):
        pass
    
        
class Event():
    
    def __init__():
        pass
        
    def _name():
        print 'hi'


def main():

    
if __name__ == "__main__":
    main()
else:
    print "hi:", __name__
