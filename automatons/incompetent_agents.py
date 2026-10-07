from falses.incon_ccde import * 
from falses.uncertainty_sim import * 

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

"""
A structure to operate k <IncompetentAgentTypeDEGD> agents that have identical 
<InconsistentFunctionTypeCCDE>s and <UncertaintySimulatorTypeGGD>s.
""" 
class IncompetentAgentGroupTypeDEGD: 

    def __init__(self,incon_func:InconsistentFunctionTypeCCDE,uncertainty_sim,prg_seq,certainty_delta_seq):

        assert len(prg_seq) == len(certainty_delta_seq) 
        for x in prg_seq: assert type(x) in {FunctionType,MethodType}

        assert is_vector(np.array(certainty_delta_seq)) 
        assert 0.0 < np.min(certainty_delta_seq) <= np.max(certainty_delta_seq) <= 1.0

        self.agents = [] 
        self.init_agents(incon_func,uncertainty_sim,prg_seq,certainty_delta_seq)
        return 

    def init_agents(self,incon_func,usim,prg_seq,certainty_delta_seq):

        self.agents.clear() 
        
        l = len(prg_seq)
        for i in range(l):
            p,c = prg_seq[i],certainty_delta_seq[i] 
            q = IncompetentAgentTypeDEGD(i,deepcopy(incon_func),deepcopy(usim),p,c) 
            self.agents.append(q) 
        return 

    def demonstrate(self,num_iter:int,ext_prng): 
        d = {}

        for x in self.agents:
            dx = x.demonstrate(num_iter,ext_prng)
            d[x.idn] = dx 
        return d 

    def execute(self):
        d = {}

        for x in self.agents:
            d[x.idn] = x.execute()
        return d 

"""
Demander agent in False Incompetence. Agent makes demands to k <IncompetentAgentTypeDEGD>s. 
"""
class FIDemander:

    def __init__(self,demand_iterations_seq,prg): 
        for d in demand_iterations_seq: assert type(d) in {int,np.int32,np.int64}  
        assert is_vector(np.array(demand_iterations_seq))
        assert type(prg) in {MethodType,FunctionType}

        self.demand_iterations_seq = demand_iterations_seq 
        self.prg = prg 

        self.demo_predict_map = dict() 
        self.accept_indices = [] 

    #----------------------- prediction phase 1 

    def recv_demonstration_dict(self,M):
        assert type(M) == dict 

        self.demo_predict_map.clear() 
        
        for idn,V in M.items():
            V_d = self.accept_contra_decisions(V)
            self.demo_predict_map[idn] = V_d 
    
    def accept_contra_decisions(self,V):
        assert len(V.shape) == 2 and V.shape[0] == 2 

        l = V.shape[1] 
        V_b = [] 
        for i in range(l): 
            q = V[0,i] 
            u = V[1,i] 

            d = prg_decimal(self.prg,[0.,1.]) 
            accept = d >= u 

            V_b.append((q,accept))

        return V_b 

    #------------------------ prediction phase 2 

    def calculate_accept_indices(self,M2): 

        c = Counter([]) 

        for idn,V in M2.items():
            I = self.choose_indices(idn,V)
            c = c + Counter(I)
        return self.majority_vote_on_indices(c,len(M2))

    def majority_vote_on_indices(self,c:Counter,num_agents): 
        assert type(c) == Counter 
        assert type(num_agents) == int and num_agents > 0 

        indices = set()
        for k,v in c.items(): 
            if v >= num_agents / 2: 
                indices |= {k} 

        self.accept_indices = sorted(indices) 
        return self.accept_indices

    def choose_indices(self,idn,V):

        V2 = self.demo_predict_map[idn]
        l = len(V) 
        assert l == len(V2) 

        indices = [] 
        for i in range(l): 
            accept,cmode = V2[i]
            a = V[i]

            expected = None 
            if cmode == -1:
                expected = a
            elif cmode = 0: 
                expected = not a 
            elif cmode == 1: 
                expected = a 
            else:
                expected = not a 
            
            # case: not accept 
            if not accept:
                expected = not expected                 

            # element expected to be True 
            if expected: 
                indices.append(i)

        return indices 

