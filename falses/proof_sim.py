from xFS_bots.graph_models.node_path import * 
from xFS_bots.graph_models.micrograph import * 
from morebs2.pr2label import * 
from morebs2.numerical_generator import prg_decimal,modulo_in_range,safe_modulo_in_range
from types import MethodType,FunctionType

"""
Proof Differential Simulator Type (S)tochastic (G)raph (T)raversal. 

Algorithm models how agents can construct different proofs (paths), 
given the same starting material (simple graphs). 
----------------------------------------------------------------------------- 

Graph `G` represents surface of decisions and connections b/t those 
decisions. `G` is how proof is constructed, via node-to-node traversal.  

Parameter `node_path_solution_seq` contains paths, each starting at 
node `start_node`, that act as the set of solutions. 

Simulator takes a PRNG `ext_prg` from an external agent, as input, and 
uses that PRNG to calculate a path P_ext of length l, l in range of 
`minmax_path_lengths`. 

Path P_ext is calculated by a graph traversal process that starts at `start_node`. 
For every current node n_c in this traversal, algorithm maps the proper decimal d, 
generated from `ext_prg`, to a neighboring node from n_c. The probabilities assigned 
to each neighbor n' of n_c is positively correlated to the normalized edge weight 
(n_c,n'). 

If P_ext is found in `node_path_soln`, external agent has constructed the same 
proof as the host. Otherwise, the (node,edge) differences between P_ext and 
`node_path_soln` are averaged out to produce a proof differential. 
"""
class ProofDifferentialSimulatorTypeSGT: 

    def __init__(self,G,start_node,edge_cost_function,node_path_solution_seq): 
        assert type(G) == defaultdict 
        assert start_node in G 
        assert type(edge_cost_function) in {MethodType,FunctionType}
        assert type(node_path_solution_seq) == list and len(node_path_solution_seq) > 0 
        for p in node_path_solution_seq: 
            assert type(p) == NodePath 
            assert p.head() == start_node 


        self.G = G 
        self.start_node = start_node 
        self.ecf = edge_cost_function
        self.node_path_soln = node_path_solution_seq

        lengths = [len(p) for p in self.node_path_soln]
        self.minmax_path_lengths = (min(lengths),max(lengths))

    """
    main method 
    """
    def exec(self,ext_prg):
        ext_path = self.external_agent_path(ext_prg)
        G0 = MicroGraph(ext_path.to_graph(True)) 

        stat = False 
        s = 0 
        for p in self.node_path_soln: 
            G1 = MicroGraph(p.to_graph(True)) 
            if G0 == G1: 
                return ext_path, 0 

            s00,s01 = G0.sub_ve_score(G1) 
            s10,s11 = G1.sub_ve_score(G0) 
            s += (s00 + s01 + s10 + s11)         
        return ext_path, s / len(self.node_path_soln)

    # NOTE: assumes edge cost function `ecf` outputs a 
    #       constant value for any edge (u,v). 
    def external_agent_path(self,ext_prg):  
        P = [self.start_node] 
        E = [] 

        R = (self.minmax_path_lengths[0],self.minmax_path_lengths[1]+1)
        path_length = modulo_in_range(int(ext_prg()),R) 
        for i in range(path_length - 1): 
            q = P[-1] 

            q2 = self.next_node(q,ext_prg) 
            if type(q2) == type(None): break 

            P.append(q2) 
            E.append(self.ecf(q,q2)) 
        return NodePath.preload(P,E) 

    def next_node(self,current_node,ext_prg):  
        L = self.next_node_pr_seq(current_node)
        if type(L) == type(None): return None 

        pr = prg_decimal(ext_prg,[0.,1.]) 
        return probability_to_label(L,pr)

    def next_node_pr_seq(self,current_node): 
        neighbors = sorted(self.G[current_node]) 
        L = [] 
        s = 0 
        for n in neighbors: 
            c = self.ecf(current_node,n)
            assert c > 0 
            L.append((n,c))
            s += self.ecf(current_node,n)

        if s == 0.0: 
            print("? strange case ? neighbor edge weights sum to 0.0. No next node.")
            return None 

        return [(c/s,n) for (n,c) in L] 

    @staticmethod
    def generate_instance(G,start_node,num_soln): 

    #def __init__(self,G,start_node,edge_cost_function,node_path_solution_seq): 


        return -1  

"""
Graph Traversal Context (C)onditional (R)educer. 

The map `n2n2n_map` that this reducer operates by 
acts as a reduction of next-node possibilities during traversal. The map 
acts as such: 
- given a node n and a neighbor node n2 that is be travelled to next, 
  algorithm selects node `n2n2n_map[n][n2]` instead. 

The nodeset of `n2n2n_map[x].keys` is the superset to the nodeset 
`n2n2n_map[x].values`. This attribute of smaller output space 
serves as the reduction process. Reduction process is the effect 
to some arbitrary context that is one of many contexts for traversal 
along the subject graph G (not included in this structure). 
"""
class GraphTraversalContextCR: 

    def __init__(self,node2neighbor2next_map): 
        assert type(node2neighbor2next_map) == dict  
        for k,v in node2neighbor2next_map.items(): 
            assert type(v) == dict 
            q = set(v.values())
            q0 = set(v.keys()) 
            assert q.issubset(q0) 

        # node -> neighbor node -> actual next 
        self.n2n2n_map = node2neighbor2next_map
        return 

    def next_node(self,current_node,next_node_):  
        try: 
            return self.n2n2n_map[current_node][next_node_] 
        except: 
            return next_node_ 

    @staticmethod 
    def generate_instance(G,output_space_ratio_range,prg):  
        assert type(G) == defaultdict 
        assert is_valid_range(output_space_ratio_range,False,True) 
        assert type(prg) in {MethodType,FunctionType}

        nodes = sorted(G.keys()) 
        D = dict() 
        prg_ = prg__single_to_int(prg) 
        for n in nodes: 
            D[n] = dict() 

            neighbors_ = sorted(G[n]) 
            neighbors = prg_seqsort(deepcopy(neighbors_),prg) 

            output_space_ratio = safe_modulo_in_range(prg(),output_space_ratio_range)
            n2 = ceil(output_space_ratio * len(neighbors)) 
            q = prg_choose_n(neighbors,n2,prg_,is_unique_picker=True)

            for (i,n3) in enumerate(neighbors_): 
                i2 = i % len(q) 
                x = q[i2]  
                D[n][n3] = x 

        return D 

"""
Proof Differential Simulator Type (C)ontextual (S)tochastic (G)raph (T)raversal. 
"""
class ProofDifferentialSimulatorTypeCSGT(ProofDifferentialSimulatorTypeSGT): 

    def __init__(self,G,start_node,edge_cost_function,node_path_solution_seq,\
        gtc_cr:GraphTraversalContextCR): 
        assert type(gtc_cr) == GraphTraversalContextCR

        super().__init__(G,start_node,edge_cost_function,node_path_solution_seq) 
        self.gtc_cr = gtc_cr 
        return 

    def next_node_pr_seq(self,current_node): 
        q = super().next_node_pr_seq(current_node)
        q = [(c,self.gtc_cr.next_node(current_node,n)) for c,n in q] 

        return q 

"""
Proof Differential Simulator Type (A)uto-(C)orrected (S)tochastic (G)raph (T)raversal. 
"""
class ProofDifferentialSimulatorTypeACSGT(ProofDifferentialSimulatorTypeCSGT):  

    def __init__(self): 
        return 