from xFS_bots.graph_models.node_path import * 
from xFS_bots.graph_models.micrograph import * 
from morebs2.pr2label import * 
from morebs2.numerical_generator import prg_decimal,modulo_in_range,safe_modulo_in_range,prg_choose_n
from types import MethodType,FunctionType
from math import ceil 

"""
Objective Type (U)ndirected (S)imple (G)raph, (M)ultiple (P)aths. 
"""
class ObjectiveTypeUSGMP: 

    def __init__(self,G,start_node,node_path_solution_seq): 
        assert type(G) == defaultdict 
        assert start_node in G 
        assert type(node_path_solution_seq) == list and len(node_path_solution_seq) > 0 
        for p in node_path_solution_seq: 
            assert type(p) == NodePath 
            assert p.head() == start_node 

        self.G = G 
        self.start_node = start_node 
        self.node_path_soln = node_path_solution_seq

        lengths = [len(p) for p in self.node_path_soln]
        self.minmax_path_lengths = (min(lengths),max(lengths))

    def average_path_length(self): 
        return np.mean([len(p) for p in self.node_path_soln])

    def head(self): 
        return self.node_path_soln[0].head() 

    def score_path(self,ext_path): 
        assert type(ext_path) == NodePath

        G0 = MicroGraph(ext_path.to_graph(True))
        s = 0 
        for p in self.node_path_soln: 
            G1 = MicroGraph(p.to_graph(True)) 
            if G0 == G1: 
                return 0 

            s00,s01 = G0.sub_ve_score(G1) 
            s10,s11 = G1.sub_ve_score(G0) 
            s += (s00 + s01 + s10 + s11)         
        return s / len(self.node_path_soln)

    """
    return: 
    - one <NodePath> in `node_path_soln` that contains `node`, index of `node` in the <NodePath>
    """
    def path_info_for_node(self,node): 

        for x in self.node_path_soln: 
            ns = x.p 
            if node in ns: 
                return x,ns.index(node)
        return None,None 

    def all_path_info_for_node(self,node): 

        q = [] 
        for x in self.node_path_soln: 
            ns = x.p 
            if node in ns: 
                q.append((x,ns.index(node))) 

        return q 


"""
Objective Type (E)xternal (F)actor (I)nfluenced (T)raversal. 

Subclass of class<ObjectiveTypeUSGMP>. 

Structure acts as the objective for an <FQSubjectTypeDD> in 
the <FalseQuestionTypeDD> automaton. Structure can be used in 
the general purpose of an objective by which an agent that is 
externally influenced attempts to execute. 
""" 
class ObjectiveTypeEFIT(ObjectiveTypeUSGMP): 

    def __init__(self,G,start_node,node_path_solution_seq): 
        super().__init__(G,start_node,node_path_solution_seq)
        
        self.current_loc = None 
        self.current_path = None 
        self.current_index = None
        
        self.fin_stat = False  
        self.npath = None 
        self.preproc() 

    def preproc(self): 
        self.current_loc = self.head()
        self.current_path,self.current_index = self.path_info_for_node(self.current_loc)  

        self.npath = NodePath(self.current_loc)

    def exec(self,counter_pr,ext_prg):  
        if self.fin_stat: return None 
        if type(self.current_index) == type(None): 
            self.fin_stat = True 
            return None 

        assert 0.0 <= counter_pr <= 1.0 

        print("LLL: ",len(self.npath),self.minmax_path_lengths[1])
        if len(self.npath) > self.minmax_path_lengths[1]: 
            self.fin_stat = True 
            return None 

        take_planned_path = bool(prg_decimal(ext_prg,[0.,1.]) < (1.0 - counter_pr)) 

        # case: take the next node in the path 
        if take_planned_path: 
            return self.next_node__planned_path()

        # case: attempt to move to a next node that is not a next 
        #       for any path containing `current_loc`. 
        return self.next_node__contra_path(ext_prg) 

    def next_node__planned_path(self): 
        i = self.current_index + 1 

        # subcase: finished traversal 
        if i >= len(self.current_path): 
            self.fin_stat = True 
            return None 
        
        next_loc = self.current_path[i] 
        self.npath.append(next_loc,1) 
        self.current_loc = next_loc 
        self.current_index += 1 
        return next_loc

    def next_node__contra_path(self,ext_prg): 
        npath_info = self.all_path_info_for_node(self.current_loc)
        possible_nexts = set() 

        for x in npath_info: 
            i = x[1] + 1 
            if i < len(x[0]): 
                possible_nexts |= {x[0][i]} 

        alt_neighbors = self.G[self.current_loc] - possible_nexts 

        # subcase: no alternative neighbors exist. Attempt to take 
        #          a next node not part of the current path 
        if len(alt_neighbors) == 0: 
            exclude_set = set() if self.current_index + 1 >= len(self.current_path) \
                else {self.current_path[self.current_index + 1]} 

            alt_neighbors = possible_nexts - exclude_set 

        alt_neighbors = sorted(alt_neighbors) 
        j = int(ext_prg()) % len(alt_neighbors) 
        next_loc = alt_neighbors[j]
        self.npath.append(next_loc,1.0)
        self.current_node,self.current_index = self.path_info_for_node(next_loc)
        return next_loc 

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
class ProofDifferentialSimulatorTypeSGT(ObjectiveTypeUSGMP): 

    def __init__(self,G,start_node,edge_cost_function,node_path_solution_seq): 
        super().__init__(G,start_node,node_path_solution_seq)

        assert type(edge_cost_function) in {MethodType,FunctionType}
        self.ecf = edge_cost_function

    """
    main method 
    """
    def exec(self,ext_prg):
        ext_path = self.external_agent_path(ext_prg)

        return ext_path, self.score_path(ext_path)

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

        return [(round(c/s,10),n) for (n,c) in L] 

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

        return GraphTraversalContextCR(D)  

"""
Proof Differential Simulator Type (C)ontextual (S)tochastic (G)raph (T)raversal. 

Extension of class<ProofDifferentialSimulatorTypeSGT> and uses class<GraphTraversalContextCR> 
to influence external agent proof construction. 
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

    def prng_update_context(self,output_space_ratio_range,prg): 
        self.gtc_cr = GraphTraversalContextCR.generate_instance(self.G,output_space_ratio_range,prg)
        return

"""
Proof Differential Simulator Type (A)uto-(C)orrected (S)tochastic (G)raph (T)raversal. 

Extension of <ProofDifferentialSimulatorTypeCSGT> with an auto-correction feature. 
Simulator constructs proof (path) by first selecting a solution P in `node_path_soln`. 


        ** Path Traversal ** 

External agent PRNG used to output decimals, and these decimals are mapped out to next 
nodes from current nodes. When the decimal d does not correspond to the correct next node, 
given solution P, auto-correction uses internal PRNG to attempt adjusting d to d' so that 
d' maps to the correct next node. If the correct next node cannot be reached, typically 
due to constraints from context of <GraphTraversalContextCR>, auto-correction defers to 
letting d map out to the wrong node n_. Algorithm then will choose another solution P' in 
`node_path_soln` if P' contains n_, so that P' is the new `current_path`. If P' is selected, 
then that would be a "path correction" (see variable<current_num_path_corrections> and 
variable<max_num_path_corrections>). There are limits to the number of path corrections that 
auto-correction can make for every call to method<exec> (path traversal <-> proof construction). 

        ** Pertinent Variables in Auto-Correction ** 
- Probability correction: `cumulative_ac_sum`, `current_ac_sum`. 
- Number of units corrected: `cumulative_ac_units`, `current_ac_units`. 
"""
class ProofDifferentialSimulatorTypeACSGT(ProofDifferentialSimulatorTypeCSGT):  

    def __init__(self,G,start_node,edge_cost_function,node_path_solution_seq,\
        gtc_cr:GraphTraversalContextCR,internal_prg,max_num_path_corrections:int=3,\
        verbose:bool=True): 

        assert type(internal_prg) in {MethodType,FunctionType} 
        assert type(max_num_path_corrections) == int and max_num_path_corrections >= 0 
        assert type(verbose) == bool 

        super().__init__(G,start_node,edge_cost_function,node_path_solution_seq,gtc_cr)
        
        self.internal_prg = internal_prg
        self.max_num_path_corrections = max_num_path_corrections
        self.verbose = verbose 

        self.current_num_path_corrections = 0

        self.cumulative_ac_sum = 0.0
        self.current_ac_sum = 0.0 

        self.cumulative_ac_units = 0 
        self.current_ac_units = 0 

        self.current_path = None 
        self.current_index = None 
        return 

    def external_agent_path(self,ext_prg):  
        self.current_ac_sum = 0.0 
        self.current_num_path_corrections = 0 

        i = int(ext_prg() + self.internal_prg()) % len(self.node_path_soln)  
        self.current_path = self.node_path_soln[i] 
        self.current_index = 0 

        P = [self.start_node] 
        E = [] 

        stat = True 
        while stat: 
            q = P[-1]
            n = self.next_node(q,ext_prg) 
            stat = type(n) != type(None) 

            if stat: 
                P.append(n) 
                E.append(self.ecf(q,n))  

            if self.verbose: 
                print("current path --> ",P) 
                print("\n")
        return NodePath.preload(P,E) 

    def next_node(self,current_node,ext_prg):
        n = self.next_node_(current_node,ext_prg) 
        if type(n) == type(None): return 

        target = self.current_path[self.current_index + 1]

        if self.verbose: 
            print("next={},current={},target={}, # corrections={}".format(n,current_node,\
                target,self.current_num_path_corrections))
            print("current reference path --> ",self.current_path.p)

        # case: target met 
        if n == target: 
            self.current_index += 1 
            return n 

        # case: target not met, 
        self.current_num_path_corrections += 1

        # subcase: exceeded maximum number of path corrections (missed target node) 
        if self.current_num_path_corrections > self.max_num_path_corrections: 
            return None 

        P,i = self.path_info_for_node(n)
        if type(P) != type(None): 
            self.current_path = P 
            self.current_index = i 
        else: 
            self.current_index += 1 

        return n 

    def next_node_(self,current_node,ext_prg): 
        ##assert self.current_path[self.current_index] == current_node 

        if self.current_index >= len(self.current_path) -1: return None 

        L = self.next_node_pr_seq(current_node)
        if type(L) == type(None): return None 

        target_node = self.current_path[self.current_index + 1] 

        pr = round(prg_decimal(ext_prg,[0.,1.]),10) 
        acorr = self.auto_correct_probability(pr,target_node,L)
        acorr_ = round(abs(acorr),10) 
        if acorr < 0: acorr = acorr_ * -1 
        else: acorr = acorr_ 
        
        pr = round(pr + acorr,10) 

        acorr_ = abs(acorr)
        self.current_ac_sum += acorr_ 
        self.cumulative_ac_sum += acorr_ 

        if acorr_ > 0: 
            self.current_ac_units += 1
            self.cumulative_ac_units += 1
        return probability_to_label(L,pr)

    def auto_correct_probability(self,pr,target_node,pr2node_seq): 
        # case: no auto-correction needed
        if probability_to_label(pr2node_seq,pr) == target_node: 
            return 0.0 

        # get all indices where target node occurs 
        indices = [] 
        for i,x in enumerate(pr2node_seq): 
            if x[1] == target_node: 
                indices.append(i) 

        # case: target node not in options 
        if len(indices) == 0: 
            return 0.0 

        # case: get the minimum absolute difference to add to pr to 
        #       correspond to `target_node`. 
        pr_seq = [p[0] for p in pr2node_seq] 
        X = np.cumsum(pr_seq) 

        X_ = np.array([X[i] for i in indices]) 
        d = X_ - pr 
        i2 = np.argmin(np.abs(d)) 
        return d[i2]