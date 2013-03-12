# -*- coding: utf-8 -*-
"""
Created on Fri Mar 01 19:14:32 2013

@author: Steve
"""

import time
import PyBasicComms
import PIDff

from PyQt4 import QtCore

from StateLib import State,Event

YAW_MIN = 50
YAW_MAX = 1000
YAW_DEF = 512
PITCH_MAX = 550
PITCH_MIN = 250
PITCH_DEF = 400

SEARCH_STEP =10


class Events():
    class TIMER_DONE(Event):
        pass
    class ALL_DONE(Event):
        pass
    class DONE_INIT(Event):
        pass


class StateMachine():
"""  A state machine.  """

    context.QUIT_FLAG = False
    
	class START(State):

		def handleEvent(self, event, context):
			if event == Events.DONE_INIT
				return self.WAIT_LONG
		def onStep(self,context):
			print "Starting..."
			

		def onEnter:
			print "entering state"
			
	
	class WAIT_LONG(State):
		def onEnter(self, context):
			self.timer_end = time.time() + 5
			print 'Started timer'
		def handleEvent(self,event,context):
			if event == self.TIMER_DONE
			     return self.END

    class END(State):
        def onEnter(self, context)::
            print "ending"
        def onStep(self, context)::
            context.QUIT_FLAG = True
            
    
    class __init__():
        
        self.state = START
        
    class run():
        context = None
        while not context.QUIT_FLAG:
            self.state.onStep(context)
            event = self.CheckForEvents(, context)
            newstate = self.state.handleEvent( event, context)
            if newstate is not None:
                state = newstate
                state.onEnter(context)
        
        
            
