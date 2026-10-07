from falses.incon_ccde import * 
from falses.uncertainty_sim import * 

class IncompetentAgentGroupTypeDEGD: 

    def __init__(self,incon_func:InconsistentFunctionTypeCCDE,uncertainty_sim,prg_seq,certainty_delta_seq):

        assert len(prg_seq) == len(certainty_delta_seq) 
        for x in prg_seq: assert type(x) in {FunctionType,MethodType}

        assert is_vector(np.array(certainty_delta_seq)) 
        assert 0.0 < np.min(certainty_delta_seq) <= np.max(certainty_delta_seq) <= 1.0

        self.agents = [] 

        return 

    def init_agents(self,incon_func,usim,prg_seq,certainty_delta_seq):

        self.agents.clear() 
        
        l = len(prg_seq)
        for i in range(l):
            p,c = prg_seq[i],certainty_delta_seq[i] 
            q = IncompetentAgentTypeDEGD(i,deepcopy(incon_func),deepcopy(usim),p,c) 
            self.agents.append(q) 
        return 

"""
Agent with simulated incompetence methodology, built from 
    <InconsistentFunctionTypeCCDE> + <UncertaintySimulatorTypeGGD>. 
Agent actions represented as boolean values. 

Agent is prompted by external party to demonstrate itself (see function<demonstrate>). 
This demonstration does not yield the actual function results from <InconsistentFunctionTypeCCDE>, 
but the contradiction mode sequence V_c that corresponds to the demonstrative actions, and 
a sequence U of corresponding certainty measures. 
NOTE: see file<falses.incon_ccde> for specific details. 

For every i'th element q of V_c, q in {-1,0,1,2}, let a_i be the actual, d_i the 
demonstrative action. Below is a table showing the results from demonstration (d) 
and execution (e). 

                d      e
    -----------------------------
    q=-1  --> 1*a_i,  1*d_i 
    q=0   --> -1*a_i, 1*d_i
    q=1   --> 1*a_i,  -1*d_i
    q=2   --> -1*a_i, -1*d_i
    ----------------------------- 

The results from <demonstrate> are then processed by the external party. The external 
party makes its decisions to accept or reject each of the demonstrative action booleans, 
and then prompts this agent to execute the actions, selecting only the indices I that 
the party determines to be favorable. 

NOTE: since this is a boolean-based agent (actions are booleans), the default is for the 
external party objective to select executive actions of TRUE. 
"""
class IncompetentAgentTypeDEGD: 

    def __init__(self,idn,incon_func:InconsistentFunctionTypeCCDE,usim:UncertaintySimulatorTypeGGD,prg,certainty_delta:float): 

        assert type(incon_func) == InconsistentFunctionTypeCCDE
        assert type(usim) == UncertaintySimulatorTypeGGD
        assert type(prg) in {FunctionType,MethodType}
        assert 0 < certainty_delta <= 1.0 

        self.idn = idn 
        self.ifunc = incon_func 
        self.usim = usim
        self.prg = prg 
        self.certainty_delta = certainty_delta

        self.default_certainty = 1.0 
        self.certainty_seq = [] 
        return 

    def demonstrate(self,num_iter:int,ext_prng): 
        self.demo_iterate(num_iter) 
        self.calculate_certainties(ext_prng) 

        q0 = deepcopy(self.ifunc.contra_seq) 
        q1 = deepcopy(self.certainty_seq) 
        return np.vstack((q0,q1))

    def execute(self): 
        return self.ifunc.exec_iterate()

    def demo_iterate(self,num_iter:int): 
        self.ifunc.demo_iterate(num_iter,self.prg)  
        return 

    def calculate_certainties(self,ext_prng): 
        self.certainty_seq.clear() 

        l = len(self.ifunc.Q) 
        for i in range(l): 
            c0 = self.usim.cmp(ext_prng) 
            contra_mode = self.ifunc.contra_seq[i] 
            self.certainty_delta(contra_mode) 
            self.certainty_seq.append((1 - self.default_certainty) * c0) 

        return 

    def certainty_delta(self,contra_mode): 

        # no contra, increase certainty 
        if contra_mode == -1: 
            self.default_certainty = self.default_certainty * (1 + self.certainty_delta)
            self.default_certainty = min([self.default_certainty,1.0]) 
            return 

        # contra, decrease certainty 
        self.default_certainty = self.default_certainty * self.certainty_delta
        return 