from xFS_bots.graph_models.node_path import * 
from xFS_bots.graph_models.micrograph import * 
from morebs2.pr2label import * 
from morebs2.numerical_generator import prg_decimal
from types import MethodType,FunctionType

"""
Proof Differential Simulator Type (S)tochastic (G)raph (T)raversal. 

Algorithm models how agents can construct different proofs (paths), 
given the same starting material (simple graphs). 
----------------------------------------------------------------------------- 

Graph `G` represents surface of decisions and connections b/t those 
decisions. `G` is where proof takes place. 

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

    def external_agent_path(self,ext_prg):  
        P = [self.start_node] 
        E = [] 

        R = (self.minmax_path_lengths[0],self.minmax_path_lengths[1]+1)
        path_length = modulo_in_range(int(ext_prg()),R) 
        for i in range(path_length - 1): 
            q = P[-1] 

            q2 = self.next_node(q,ext_prg) 
            P.append(q2) 
            E.append(self.ecf(q,q2)) 
        return NodePath.preload(P,E) 


    def next_node(self,current_node,ext_prg):  
        neighbors = sorted(self.G[current_node]) 
        L = [] 
        s = 0 
        for n in neighbors: 
            c = self.ecf(current_node,n)
            L.append((n,c))
            s += self.ecf(current_node,n)

        if s == 0.0: 
            print("? strange case ? neighbor edge weights sum to 0.0. No next node.")
            return None 

        L = [(c/s,n) for (n,c) in L] 
        pr = prg_decimal(ext_prg,[0.,1.]) 
        return probability_to_label(L,pr)

"""
Proof Differential Simulator Type (C)ontextual (S)tochastic (G)raph (T)raversal. 
"""
class ProofDifferentialSimulatorTypeCSGT(ProofDifferentialSimulatorTypeSGT): 

    def __init__(self): 
        return 

"""
Proof Differential Simulator Type (A)uto-(C)orrected (S)tochastic (G)raph (T)raversal. 
"""
class ProofDifferentialSimulatorTypeACSGT(ProofDifferentialSimulatorTypeCSGT):  

    def __init__(self): 
        return 