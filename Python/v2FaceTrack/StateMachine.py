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



class StateMachine():
""  A state machine.  

""
	class START(State):

		def handleEvent(self, event, context):
			if event == self.DONE_INIT
				return self.WAIT_LONG
		def onStep(self,context):
			print "Starting..."
			return self.DONE_INIT

		def onEnter:
			print "entering state"
			
	
	class WAIT_LONG(State):
		def onEnter:
			timer_end = time.time() + 5
			print 'Started timer'
		def handleEvent(self,event,context):
			if event == self.TIMER_DONE
			     return self.END

