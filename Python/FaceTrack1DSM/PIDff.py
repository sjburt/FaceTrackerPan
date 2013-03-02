# -*- coding: utf-8 -*-
"""
PIDFF,  a PID control with forward propogation. 

Created on Fri Mar 01 14:19:04 2013

@author: Steve
"""


class PIDff:
    
    def __init__(self, P=2.0, I=0.0, D=1.0, depth=2,errFF=.95, Derivator=0, Integrator=0, Integrator_max=500, Integrator_min=-500):

        self.Kp=P
        self.Ki=I
        self.Kd=D
        self.Derivator=Derivator
        self.Integrator=Integrator
        self.Integrator_max=Integrator_max
        self.Integrator_min=Integrator_min

        self.kerrFF = errFF
        self.depth = depth
        self.depthbuffer = list()
        for i in range(self.depth):
            self.depthbuffer.append(0)
            
        self.set_point=0.0
        self.error=0.0

    def update(self,current_value):
        """
        Calculate PID output value for given reference input and feedback
        """

        self.error = self.set_point - current_value

        self.P_value = self.Kp * self.error
        self.D_value = self.Kd * ( self.error - self.Derivator)
        self.Derivator = self.error

        self.Integrator = self.Integrator + self.error

        if self.Integrator > self.Integrator_max:
            self.Integrator = self.Integrator_max
        elif self.Integrator < self.Integrator_min:
            self.Integrator = self.Integrator_min

        self.I_value = self.Integrator * self.Ki
        
        FF_val = self.kerrFF * sum(self.depthbuffer) / self.depth       
        
        PID = self.P_value + self.I_value + self.D_value - FF_val
        
        self.depthbuffer.pop(0)
        self.depthbuffer.append(PID)

        return PID

    def setPoint(self,set_point):
        """
        Initilize the setpoint of PID
        """
        self.set_point = set_point
        self.Integrator=0
        self.Derivator=0

    def setIntegrator(self, Integrator):
        self.Integrator = Integrator

    def setDerivator(self, Derivator):
        self.Derivator = Derivator

    def setKp(self,P):
        self.Kp=P

    def setKi(self,I):
        self.Ki=I

    def setKd(self,D):
        self.Kd=D

    def setKerFF(self,erff):
        self.KerFF=erff
    
    def getPoint(self):
        return self.set_point

    def getError(self):
        return self.error

    def getIntegrator(self):
        return self.Integrator

    def getDerivator(self):
        return self.Derivator
        
