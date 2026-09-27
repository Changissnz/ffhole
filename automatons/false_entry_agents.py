from falses.false_entry_functions import * 
from .graph_comp_ext import * 
from xFS_bots.graph_models.node_path import * 

DEFAULT_FE_SURFACE_N2N_NUM_PATHS = 7 

class FENode: 

    def __init__(self,idn,weight):   
        self.idn = idn 
        self.weight = weight
        self.weight_appearance = weight 
        self.trap_stat = False 
        return

    #-------------------------------

    def activate_trap(self): 
        self.trap_stat = True 
        return

    #------------------------------- 

    def reset(self): 
        self.weight_appearance = self.weight 
        self.trap_stat = False 
        ##self.other_support.clear() 
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

        # minimum paths; (source node, target node) -> [<NodePath>] 
        self.min_paths = dict()  

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
            node_map[x] = FENode(x,w) 

        return FESurface(G,set(entry_points),set(end_points),node_map,max_computation_size,prg)

    def appearance(self): 
        return {idn:v.weight_appearance for idn,v in self.node_map.items()} 

    """
    agent_hypotheses_map := dict, agent idn -> expected range of support for next node
    """
    def load_agent_hyp_map(self,agent_hypotheses_map): 
        assert type(agent_hypotheses_map) == dict 
        for v in agent_hypotheses_map.values(): 
            assert is_valid_range(v,True,True) or is_valid_range(v,False,True) 
        self.agent_next_hyp_map = agent_hypotheses_map 
        return

    #-------------------------- external agent info update

    def trapped_nodes(self): 
        tn = set() 
        for n in self.occupied_nodes.keys(): 
            neighbors = self.G[n] 
            q = set([self.node_map[n_].trap_stat for n_ in neighbors]) 

            if q == {True}: 
                tn |= {n}  

        return tn 

    def remove_trapped_agents(self): 
        tn = self.trapped_nodes()
        print("trapped nodes")
        print(tn)
        agents = set() 
        for t in tn: 
            agents |= self.occupied_nodes[t] 
            del self.occupied_nodes[t] 

        for v in self.node_map.values(): v.reset() 
        return agents 

    def passed_agents(self): 
        passed = set()
        for x in self.end_points: 
            q = self.occupied_nodes[x] 
            passed |= deepcopy(q) 
            del self.occupied_nodes[x] 
        return passed 

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
                M2[k] = deepcopy(self.entry_points) 
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

    def select_trap(self): 
        q,q1 = self.candidate_agent_locations()
        i = int(self.prg()) % len(q) 
        return q[i] 

    def candidate_agent_locations(self): 
        a2next_map = self.agent_to_possible_next_map__nonends()  
        agent_idns,nextseq_seq = self.sort_agent_to_possible_next_map(a2next_map) 
        q = OrderedSelection(nextseq_seq) 
        return self.fetch_best_traps(agent_idns,q)

    def fetch_best_traps(self,agent_idns,ord_selector:OrderedSelection): 

        best_traps = [] 
        best_score = -float('inf') 
        c = 0 
        while c < self.max_computation_size: 
            x = next(ord_selector)
            if type(x) == type(None): break 
            agent_locations = {agent_idns[i]:x_ for i,x_ in enumerate(x)}

            T,score = self.compute_trap(agent_locations) 

            if score > best_score: 
                best_traps.clear() 
            
            if score >= best_score: 

                best_traps.extend([(t,agent_locations) for t in T]) 
                best_score = score 
            c += 1 
        return best_traps,best_score 

    def compute_trap(self,agent2next_map): 
        app_weight = self.appearance()
        q = {agent2next_map[k]:v for k,v in self.agent_next_hyp_map.items()} 


        best_traps,best_score = max_traps_with_boolean_conditional(\
            self.G,agent2next_map,q,\
            app_weight,self.prg,self.max_computation_size)

        return best_traps,best_score 

    #------------------------------------ used by False Entry to send weight-range hypotheses to agent 

    def min_paths_from_entry_to_end(self,entry,end): 
        assert entry in self.entry_points and end in self.end_points

        if (entry,end) not in self.min_paths: 
            F = BDFSCache(entry,self.G,is_bfs=True,prg=self.prg,edge_cost_function= DEFAULT_EDGE_COST_FUNCTION_2,\
            num_paths_per_node=DEFAULT_FE_SURFACE_N2N_NUM_PATHS,max_search_radius=float('inf')) 
            F.exec() 

            for k,v in F.min_paths.items(): 
                self.min_paths[(entry,k)]  = v 

        return self.min_paths[(entry,end)]

    def prg_choose_paths_to_endpoint_from_entry(self,entry): 

        # choose an endpoint 
        ep = sorted(self.end_points)
        i = int(self.prg()) % len(ep) 
        end = ep[i] 
        return self.min_paths_from_entry_to_end(entry,end)

    def node_associated_weights(self,n): 
        # case: node is entry point, compare it with other entry points 
        if n in self.entry_points: 
            Q = self.entry_points 

        # case: node is not entry point, compare it with neighbors 
        else: 
            Q = self.G[n] 
    
        return [self.node_map[n2].weight for n2 in Q] 

    def prg_weight_range_for_node(self,n,ambiguity): 
        weights = self.node_associated_weights(n)

        assert len(weights) >= 1 

        num_weights_in_span = 1 
        if len(weights) > 1: 
            x = 1 / (len(weights) - 1) 
            p = round(ambiguity / x) 
            num_weights_in_span += p 

        return prg_choose_subrange_for_n_elements(weights,num_weights_in_span,self.prg,\
            starting_index = None,default_zero_distance=5.0,default_zero_diameter=1.0) 

    def prg_weight_range_hypothesis_from_path(self,p,ambiguity:float): 
        assert type(p) == NodePath 
        assert len(p) > 1 
        assert p[0] in self.entry_points

        W = [] 
        for i in range(len(p)): 
            w = self.prg_weight_range_for_node(p[i],ambiguity) 
            W.append(tuple(w))
        return W 

    def prg_choose_weight_range_hypothesis_for_entry(self,entry,hyp_type,ambiguity:float): 
        assert hyp_type in {"set","seq"} 
        assert 0. <= ambiguity <= 1. 

        paths = self.prg_choose_paths_to_endpoint_from_entry(entry) 

        i = int(self.prg()) % len(paths) 
        p = paths[i] 

        weight_ranges = self.prg_weight_range_hypothesis_from_path(p,ambiguity)

        if hyp_type == "set": 
            return prg_weight_range_seq_to_set__type_intersection(weight_ranges,prg)
        return weight_ranges  
    
    #--------------------------------------------------------------------- 

    def project_appearance(self):
        q = self.select_trap() 

        for k,v in q[0].items(): 
            self.node_map[k].weight_appearance = v 
        self.set_trap(q[1])
        return self.appearance() 

    def agent_location_to_appeared_node_weights(self,loc): 
        A = self.appearance() 

        if type(loc) == type(None): 
            neighbors = self.entry_points
        else: 
            neighbors = self.G[loc]
        return {n:A[n] for n in self.entry_points} 

    def update_agent_locations(self,a2l_map): 
        self.occupied_nodes.clear() 
        for k,v in a2l_map.items():
            self.occupied_nodes[v] |= {k} 

    #------------------------------------------ executing trap 

    def set_trap(self,a2node_map):  
        nodes = set(a2node_map.values()) 

        for n in nodes: 
            neighbors = self.G[n] 
            for n_ in neighbors: self.node_map[n_].activate_trap() 

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

    def __init__(self,idn,weight_hypothesis,end_points,prg): 
        assert type(end_points) == set 
        self.idn = idn 
        self.hyp = FEAHyp(weight_hypothesis,prg) 
        self.end_points = end_points
        self.node_loc = None 
        self.prg = prg 

        self.next_wr = None 
        return

    def set_next_weight_range(self): 
        q = next(self.hyp)

        # case: choose one in sequence 
        if type(q) == list: 
            i = int(self.prg()) % len(q) 
            self.next_wr = q[i] 
            return q[i] 
        self.next_wr = q 
        return q 


    def choose_next_loc(self,node_weight_map): 
        assert type(self.next_wr) != type(None) 

        # case: one of the node neighbors is an endpoint; take it. 
        end_points_ = set(node_weight_map.keys()).intersection(self.end_points) 
        if len(end_points_) > 0: 
            end_points_ = sorted(end_points_) 
            i = int(self.prg()) % len(end_points_) 
            n = end_points_[i]
            self.update_loc(n) 
            return n 

        candidates = set() 

        for k,v in node_weight_map.items(): 
            if self.next_wr[0] <= v <= self.next_wr[1]: 
                candidates |= {k} 

        candidates = sorted(candidates)

        # case: no candidates, choose one using PRNG 
        if len(candidates) == 0: 
            candidates = sorted(node_weight_map.keys())

        i = int(self.prg()) % len(candidates) 
        n = candidates[i]  
        self.update_loc(n) 
        return n 

    def update_loc(self,n): 
        self.node_loc = n
        return 

class FEAgentSpawn: 

    def __init__(self,prg,hyp_type,end_points):
        assert type(prg) in {MethodType,FunctionType} 
        assert hyp_type in {"set","seq"} 
        assert type(end_points) == set 

        self.prg = prg 
        self.hyp_type = hyp_type
        self.end_points = end_points
        self.agents = [] 
        self.acount = 0 
        return 

    def spawn_from_hyp(self,hyp): 
        q = self.acount
        self.acount += 1  
        return FEAgent(q,hyp,deepcopy(self.end_points),self.prg)