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

        self.preproc() 
        return 

    def preproc(self): 

        self.paths,components = BDFSCache.BFS_full(self.G,nodeset=None,return_type="paths",\
            prg=self.prg,max_search_radius=float('inf'),edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,\
            verbose=False)
        assert len(components) == 1 
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

    def induce_answer(self,a_idn): 
        nodes = sorted((set(self.G.keys()) - {a_idn}).intersection(\
            set(self.agent2exp_map.keys()))) 

        node_distances = [] 
        for n in nodes: 
            q = self.paths[(a_idn,n)].cost() 
            node_distances.append((n,q)) 

        if len(node_distances) == 0: return None 

        ref_node = prg_seqsort_ties(node_distances,self.prg,lambda x:x[1])[0][0] 
        return self.agent2exp_map[ref_node]

    def update_answer(self,a_idn,answer_type): 
        return -1 