from .graph_node_labeller import * 

"""
Inconsistent Function Type (E)xpected (S)warm (A)gent (R)esponse. 

Used as a system for answering individual agents, comprising a swarm, 
on an arbitrary question. 
"""
class InconsistentFunctionTypeESAR: 

    def __init__(self,default_ans,agent2exp_map,agent2recv_map,agent_relation_graph,prg):

        assert type(agent_relation_graph) == defaultdict 
        assert set(agent2exp_map.keys()).issubset(set(agent_relation_graph.keys()))
        assert set(agent2recv_map.keys()).issubset(set(agent_relation_graph.keys()))
        assert type(prg) in {MethodType,FunctionType}

        # singleton 
        self.default_ans = default_ans 
        # agent idn -> expected answer by agent  
        self.agent2exp_map = agent2exp_map
        # agent idn -> most recent answer received from agent  
        self.agent2recv_map = agent2recv_map
        # defaultdict, graph 
        self.arg = agent_relation_graph
        self.prg = prg 

        # agent idn -> number of times expected answer changes 
        self.inconsistency_count = defaultdict(int)
        return 

    """
    main method

    Choose to answer agent `a_idn` with either expected or 
    consistent (most recent) answer. 
    """
    def answer(self,a_idn): 
        if a_idn not in self.agent2exp_map: 
            return self.default_ans 
        elif type(self.agent2exp_map[a_idn]) == type(None): 
            return self.default_ans 
        
        d0 = prg_decimal(self.prg,[0.,1.]) 
        d1 = prg_decimal(self.prg,[0.,1.]) 

        # choose expected 
        if d0 >= d1: 
            return self.agent2exp_map[a_idn] 
        # choose consistent 
        return self.consistent_answer(a_idn) 

    def consistent_answer(self,a_idn): 
        if a_idn in self.agent2recv_map: 
            return self.agent2recv_map[a_idn]
        return self.default_ans  

    def update_answer(self,a_idn,ans,answer_type): 
        assert answer_type in {"exp","sent"} 
        Q = self.agent2exp_map if answer_type == "exp" else self.agent2recv_map

        if answer_type == "exp": 
            if Q[a_idn] != ans: self.inconsistency_count[a_idn] += 1 

        Q[a_idn] = ans 
        return