from falses.false_entry_functions import * 
from .graph_comp_ext import * 

class FENode: 

    def __init__(self,idn,weight,trap_node= None):   
        self.idn = idn 
        self.weight = weight
        self.weight_appearance = weight 
        ##self.edge_weights = edge_weights
        self.trap_node = trap_node

        self.other_support = set() 
        return

    #-------------------------------

    def activate_trap(self,node_idn): 
        self.trap_node = node_idn 
        return

    def call_trap(self): 
        q = self.trap_node 
        self.trap_node = None 
        return q,self.weight  

    #------------------------------- 

    def reset_support(self): 
        self.weight_appearance = self.weight 
        self.other_support.clear() 
        return

    def conduct_support_for_other_node(self,fe_node:FENode,support:float):  
        assert type(fe_node) == FENode 

        if self.weight_appearance <= 0.: 
            print("cannot support any more.")
            return 

        if support > self.weight_appearance: 
            support = self.weight_appearance 

        self.fe_node.weight_appearance += support 
        self.weight_appearance -= support

        self.other_support |= {self.fe_node.idn} 
        return 

class FESurface: 

    def __init__(self,G,entry_points,end_points,node_map,max_computation_size:int,prg):   
        assert set(G.keys()) == set(node_map.keys())
        assert entry_points.issubset(set(G.keys()))
        assert end_points.issubset(set(G.keys()))
        assert type(max_computation_size) == int and max_computation_size > 0 
        assert type(prg) in {MethodType,FunctionType} 

        self.G = G 
        self.entry_points = entry_points
        self.end_points = end_points
        self.node_map = node_map
        self.max_computation_size = max_computation_size 
        self.prg = prg 

        # node -> set of agents 
        self.occupied_nodes = defaultdict(set)

        # agent idn -> expected range of support for next node 
        self.agent_next_hyp_map = dict() 

    @staticmethod
    def generate_instance(G,node_weight_range,num_entry,num_endpoints,max_computation_size,prg):  

        assert len(G) >= num_entry + num_endpoints
        assert graph_component_size(G) == 1 

        assert is_valid_range(node_weight_range,True,True) or \
            is_valid_range(node_weight_range,False,True)

        assert 0 < num_entry 
        assert 0 < num_endpoints

        assert type(prg) in {MethodType,FunctionType} 

        entry_points = prg_choose_connected_component(G,num_entry,prg)

        end_points = prg_choose_farthest_endpoints_from_nodeset(\
            G,entry_points,num_endpoints,prg)

        V = sorted(G.keys())

        node_map = {} 
        for x in V: 
            w = safe_modulo_in_range(prg(),node_weight_range)
            node_map[x] = FENode(x,w,None) 

        return FESurface(G,set(entry_points),set(end_points),node_map,max_computation_size,prg)

    def appearance(self): 
        return {idn:v.weight_appearance for idn,v in self.node_map.items()} 

    """
    agent_hypotheses_map := dict, agent idn -> expected range of support for next node
    """
    def load_agent_hyp_map(self,agent_hypotheses_map): 
        assert type(agent_hypotheses_map) == dict 
        for v in agent_hypotheses_map.values(): assert is_valid_range(v,True,False) or is_valid_range(v,False,False) 
        self.agent_next_hyp_map = agent_hypotheses_map 
        return

    #-------------------------- agent-to-node mapping functions 

    def agent2node_map(self): 
        M = invert_map__seqvalue(self.occupied_nodes) 
        M = {k:v[0] for k,v in M.items()} 

        q = set(self.agent_next_hyp_map.keys()) - set(M.keys()) 
        for q_ in q: 
            M[q_] = None 
        return M

    def agent_to_possible_next_map(self): 
        M = self.agent2node_map()
        M2 = dict() 

        for k,v in M.items(): 
            if type(v) == type(None): 
                M2[k] = deepcopy(v2) 
            else: 
                M2[k] = deepcopy(self.G[v])

        return M2 

    def agent_to_possible_next_map__nonends(self): 
        # get possible next 
        agent_possible_next = self.agent_to_possible_next_map() 

        # remove endpoints from possible next 
        for k in agent_possible_next.keys(): 
            v = agent_possible_next[k] 
            v -= self.end_points
        return agent_possible_next

    #------------------------------------ selecting next-node traps for agents 

    def sort_agent_to_possible_next_map(self,a2next_map): 
        agent_idns = sorted(a2next_map.keys()) 
        agent_idns = prg_seqsort(agent_idns,self.prg) 

        nextseq_seq = [] 
        for k in agent_idns: 
            v = a2next_map[k] 
            v_ = prg_seqsort(sorted(v),self.prg) 
            nextseq_seq.append(v_) 

        return agent_idns,nextseq_seq

    def select_wanted_agent_locations(self): 
        a2next_map = self.agent_to_possible_next_map__nonends()  
        agent_idns,nextseq_seq = self.sort_agent_to_possible_next_map(a2next_map) 
        q = OrderedSelection(nextseq_seq) 
        return self.fetch_best_traps(agent_idns,q)

    def fetch_best_traps(self,agent_idns,ord_selector:OrderedSelection): 

        best_traps = [] 
        best_score = -float('inf') 

        while c < self.max_computation_size: 
            x = next(ord_selector)
            if type(x) == type(None): break 
            agent_locations = {agent_idns[i]:x_ for i,x_ in enumerate(x)}

            T,score = self.compute_trap(agent_locations) 

            if score > best_score: 
                best_traps.clear() 
            
            if score >= best_score: 
                best_traps.extend(T) 
                best_score = score 
            c += 1 
        return best_traps,best_score 

    def compute_trap(self,agent2next_map): 
        app_weight = self.appearance()
        best_traps,best_score = max_traps_with_boolean_conditional(\
            self.G,agent2next_map,self.agent_next_hyp_map,\
            app_weight,self.prg)

        return best_traps,best_score 
    
    #--------------------------------------------------------------------- 

    def exec_trap(self,T):

        return -1 

    def project_appearance(self):
        return -1

class FEAHyp: 

    def __init__(self,range_info,prg):
        assert type(range_info) in {list,set} 
        for x in range_info: assert type(x) == tuple and \
            (is_valid_range(x,True,True) or is_valid_range(x,False,True)) 
        assert type(prg) in {FunctionType,MethodType}

        self.range_info = range_info 

        self.hyp_type = "set" if type(self.range_info) == set else "seq" 
        self.prg = prg 
        self.index = 0

    def __next__(self): 
        if self.hyp_type == "set": 
            return sorted(self.range_info) 
        
        if self.index >= len(self.range_info): 
            return deepcopy(self.range_info) 
        
        q = self.range_info[self.index] 
        self.index += 1 
        return q 

class FEAgent: 

    def __init__(self,weight_hypothesis,end_points,prg): 
        assert type(end_points) == set 

        self.hyp = FEAHyp(weight_hypothesis,prg) 
        self.end_points = end_points
        self.node_loc = None 
        self.prg = prg 
        return

    def choose_next_weight_range(self): 
        q = next(self.hyp)

        # case: choose one in sequence 
        if type(q) == list: 
            i = int(self.prg()) % len(q) 
            return q[i] 
        return q 


    def choose_next_loc(self,node_to_weight_map): 
        
        # case: one of the node neighbors is an endpoint; take it. 
        end_points_ = set(node_to_weight_map.keys()).intersection(self.end_points) 
        if len(end_points_) > 0: 
            end_points_ = sorted(end_points_) 
            i = int(self.prg()) % len(end_points_) 
            n = end_points_[i]
            self.update_loc(n) 
            return n 

        candidates = set() 
        weight_range = self.choose_next_weight_range() 

        for k,v in node_weight_map.items(): 
            if weight_range[0] <= v <= weight_range[1]: 
                candidates |= {k} 

        # case: no candidates, choose one using PRNG 
        candidates = sorted(candidates)

        if len(candidates) == 0: 
            candidates = sorted(node_weight_map.keys())

        i = int(prg()) % len(candidates) 
        n = candidates[i]  
        self.update_loc(n) 
        return n 

    def update_loc(self,n): 
        self.node_loc = n
        return 
