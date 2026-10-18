from .graph_node_labeller import * 

"""
Inconsistent Function Type (E)xpected (S)warm (A)gent (R)esponse. 
"""
class InconsistentFunctionTypeESAR: 

    def __init__(self,default_ans,agent2exp_map,agent2recv_map,agent_relation_graph,prg):

        assert type(agent_relation_graph) == defaultdict 
        assert set(agent2exp_map.keys()).issubset(set(agent_relation_graph.keys()))
        assert set(agent2recv_map.keys()).issubset(set(agent_relation_graph.keys()))
        assert type(prg) in {MethodType,FunctionType}

        self.default_ans = default_ans 
        self.agent2exp_map = agent2exp_map
        self.agent2recv_map = agent2recv_map
        self.arg = agent_relation_graph
        self.prg = prg 
        return 

    def answer(self,a_idn): 
        if a_idn not in self.agent2exp_map: 
            return self.default_ans 
        elif type(self.agent2exp_map[a_idn]) == type(None): 
            return self.default_ans 
        
        d0 = prg_decimal(self.prg(),[0.,1.]) 
        d1 = prg_decimal(self.prg(),[0.,1.]) 

        # choose expected 
        if d0 >= d1: 
            return self.agent2exp_map[a_idn] 
        return self.consistent_answer(a_idn) 

    def consistent_answer(self,a_idn): 
        if a_idn in self.agent2recv_map: 
            return self.agent2recv_map[a_idn]
        return self.default_ans  

    def update_answer(self,a_idn,ans,answer_type): 
        assert answer_type in {"exp","sent"} 
        Q = self.agent2exp_map if answer_type == "exp" else self.agent2recv_map
        Q[a_idn] = ans 
        return