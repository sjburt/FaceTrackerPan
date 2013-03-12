# -*- coding: utf-8 -*-
"""
Statelib
Created on Fri Mar 08 21:57:36 2013

@author: Steve

"""

class State():
    def printType(self):
        print type(self)
        print self



class dumb(State):
    dumb = "dumb"


def main():
    hi = dumb();
    
    print hi.printType()
    
    
if __name__ == "__main__":
    main()
    print State().printType
else:
    print "hi:", __name__
