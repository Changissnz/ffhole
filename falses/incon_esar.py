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

    def answer_agent(self,a_idn,prefer_consistent_answer:bool=False,answer_default:bool=False): 
        if answer_default: 
            assert type(self.default_ans) != type(None)
            return self.default_ans 

        if prefer_consistent_answer: 
            q = self.consistent_answer(a_idn) 
            if type(q) != type(None): return q 

        # if answer exists in `agent2exp_map` 
        if a_idn in self.agent2exp_map: 
            return self.agent2exp_map[a_idn] 

        # try inducing answer from closest neighbor that has an expected answer 
        return self.induce_answer(a_idn)

    def consistent_answer(self,a_idn): 
        if a_idn in self.agent2recv_map: 
            return self.agent2recv_map[a_idn]
        return None 

    def update_answer(self,a_idn,ans,answer_type): 
        assert answer_type in {"exp","sent"} 
        Q = self.agent2exp_map if answer_type == "exp" else self.agent2recv_map
        Q[a_idn] = ans 
        return