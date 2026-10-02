"""
(B)ase + (S)upport / (O)bservation + (A)ction Frame. 

A general framework for multi-agent activity, featuring a surface that is 
observed by 1+ agents and acted against. 
"""
class BSOAFrame: 

    def __init__(self,surface,bfunc,sfunc,sfunc2,ofunc,afunc):  
        self.surface = surface 
        self.bfunc = bfunc 
        self.sfunc = sfunc 
        self.sfunc2 = sfunc2 
        self.ofunc = ofunc 
        self.afunc = afunc  
        self.base_summ = None 
        return 

    def process_one(self,A): 
        self.summarize_base() 
        self.calculate_support_on_base(A) 
        self.process_agent_observation(A) 
        self.recv_action_on_surface(A) 

    def summarize_base(self,A): 
        self.base_summ = self.bfunc(self.surface,A)
        return self.base_summ

    def calculate_support_on_base(self,A):
        q = self.sfunc(self.surface,self.base_summ) 
        return self.sfunc2(A,q)

    def process_agent_observation(self,A): 
        return self.ofunc(A) 

    def recv_action_on_surface(self,A): 
        return self.afunc(self.surface,A)