from .dag_secret import * 
from seqbuild.intigers.mod_prng import * 
from morebs2.numerical_generator import prg_safe_uniform_partition_sequence,prg__constant 


#----------------------------------------- variables + functions used for <ffhole>'s 
# defined Action Graph, directed acyclic graphs extended with linear threshold functions 
# assigned to each node. Action Graphs constitute the first half of Bi-DAG intra-actions. 

DEFAULT_ACTION_DAG_NUM_LAYERS_RANGE = [54,151]
DEFAULT_ACTION_DAG_NUM_NODE_RANGE_PER_LAYER = [6,13] 

DEFAULT_ACTION_DAG_NUM_VARS_RATIO_RANGE = [0.2,0.85] 
DEFAULT_ACTION_DAG_NODE_WEIGHT_RANGE = [1.0,113.0]

DEFAULT_ACTION_DAG_PRNG_CYCLE_LENGTH_RANGE = [12,24] 

"""
uses a PRNG to generate a weight function, `wfunc`, for use with class<ExtendedDAGTypeLTPN>. 
"""
def node_to_weight_vector_function__type_NAIC(prg,cycle_length,weight_range,n2vsize_map:dict): 

    assert type(cycle_length) == int and cycle_length > 1 
    assert is_valid_range(weight_range,True,True) or is_valid_range(weight_range,False,True)
    assert weight_range[0] > 0 

    C = prg__single_to_nvec(prg,cycle_length)() 

    X = NoiseAddedIterableContainer(C,v=None) 
    X.started = True 
    ##prg_ = wrap_ranged_modulo_over_generator(prg,r)

    def f(n):  
        assert n in n2vsize_map 
        sz = n2vsize_map[n] 

        X.reset(reset_index=True,v=n) 

        return prg__single_to_nvec(X.__next__,sz)()

    return f  

"""
uses a PRNG to generate a variable subset function, `vfunc`, for use with class<ExtendedDAGTypeLTPN>. 
"""
def node_to_variable_subset_function__type_NAIC(prg,varset,subset_size_ratio_range,cycle_length): 
    assert type(varset) == set and len(varset) > 1 
    assert is_valid_range(subset_size_ratio_range,False,True) 
    
    varseq = sorted(varset) 
    C = prg__single_to_nvec(prg,cycle_length)() 

    X = NoiseAddedIterableContainer(C,v=None) 
    X.started = True 

    def f(n): 
        X.reset(reset_index=True,v=n) 

        d0 = next(X) 
        d1 = next(X) 
        r = safe_modulo_in_range(zero_div(d0,d1,0.5),subset_size_ratio_range) 

        sz = ceil(len(varseq) * r)

        varset_ = prg_choose_n(deepcopy(varseq),sz,X.__next__,is_unique_picker=True)
        return varset_ 

    return f 

"""
uses the global variables at the beginning of this file, as default parameters to 
generate an Action Graph, of type class<ExtendedDAGTypeLTPN>. 
"""
def generate_std_action_DAG(prg,varset,num_layers_range=DEFAULT_ACTION_DAG_NUM_LAYERS_RANGE,\
    num_nodes_per_layer_range=DEFAULT_ACTION_DAG_NUM_NODE_RANGE_PER_LAYER): 

    assert type(varset) == set and len(varset) > 1 

    dag = SecretSpaceTypeDAG.generate_std_instance(prg,output_is_generator=False,\
        num_layers_range=num_layers_range,num_nodes_per_layer_range=num_nodes_per_layer_range)

    nodeseq = sorted(dag.G.keys())

    cycle_length = modulo_in_range(int(prg()),DEFAULT_ACTION_DAG_PRNG_CYCLE_LENGTH_RANGE)

    vfunc = node_to_variable_subset_function__type_NAIC(prg,varset,DEFAULT_ACTION_DAG_NUM_VARS_RATIO_RANGE,\
        cycle_length)

    n2vsize_map = dict() 
    for k in dag.G.keys(): 
        n2vsize_map[k] = len(vfunc(k)) 

    cycle_length2 = modulo_in_range(int(prg()),DEFAULT_ACTION_DAG_PRNG_CYCLE_LENGTH_RANGE)
    wfunc = node_to_weight_vector_function__type_NAIC(prg,cycle_length2,\
        weight_range=DEFAULT_ACTION_DAG_NODE_WEIGHT_RANGE,n2vsize_map=n2vsize_map) 

    def tfunc(n):
        return prg__constant(0.5) 

    return ExtendedDAGTypeLTPN(dag.G,dag.l2n_map,vfunc,wfunc,tfunc,check_input_graph=False)


#----------------------- the second half (hidden-state) of Bi-DAG intra-actions. 

"""
(D)irected (A)cyclic (G)raph Traversal Function Type (H)idden (S)tate (D)irected. 

Uses a reference directed acyclic graph `dag` and a PRNG of type class<NoiseAddedIterableContainer> 
from project<seqbuild> for decision-making. This PRNG, by its design + usage, will always output 
the same number sequence for any node `n`, so that the method<next_from_node> is guaranteed to 
be consistent in output: output for `n` at any two different instances of usage output the same 
next node. 

A Bi-DAG operator, when given a `hidden_state_map` corresponding to `dag`, calculates the next 
node n' XOR NULL from n; n,n' in `dag2`, another directed acyclic graph.
"""
class DAGTraversalFunctionTypeHSD: 

    def __init__(self,dag:DAGraphContainer,prng_struct:NoiseAddedIterableContainer):
        assert type(dag) == DAGraphContainer

        self.dag = dag 
        self.prng_struct = None 
        self.load_prng_struct(prng_struct)

    def load_prng_struct(self,prng_struct:NoiseAddedIterableContainer): 
        assert type(prng_struct) == NoiseAddedIterableContainer
        self.prng_struct = prng_struct
        self.prng_struct.started = True 
        self.prng_struct.reset(reset_index=True,v=None)

    """
    main method #1 

    The `hidden_state_map` is a map, 
        state -> label set, 
    corresponding to `dag`. Function maps `n` of `dag2` to 
    the next node (proper child) or None if leaf. 
    """
    def next_from_node(self,hidden_state_map,dag2,n):
        assert type(dag2) == DAGraphContainer
        assert n in dag2.G 

        C = dag2.children_of_node(n,True) 
        if len(C) == 0: return None 

        # certainly the only child 
        if len(C) == 1: 
            return C.pop() 

        self.prng_struct.reset(reset_index=True,v=n) 
        prg = self.prng_struct.__next__

        # make the partition, node-to-integer map 
        levels = sorted(self.dag.l2n_map.keys()) 
        node2int_map = dict() 
        for l in levels: 
            l_nodeset = sorted(self.dag.l2n_map[l]) 
            prt = prg_safe_uniform_partition_sequence(l_nodeset,len(C),prg,distribute_remainder_evenly=True)

            for (i,p) in enumerate(prt): 
                for p_ in p: 
                    node2int_map[p_] = i 

        # sum up hidden state map by mapped integers 
        s = 0 
        for k,v in hidden_state_map.items(): 
            for v_ in v: 
                s += node2int_map[v_] 

        index = s % len(C) 
        return sorted(C)[index]

#----------------------------------------- a hypothesis structure used by observers of Bi-DAG 
# activity, in order to induce its hidden state. 

"""
State Induction Type (M)ost (F)requent (U)nless (C)ertain. 
"""
class StateInductionTypeMFUC: 

    def __init__(self,state_set:set,initial_hs_hyp:defaultdict=defaultdict(set)): 
        assert type(state_set) == set 
        assert type(initial_hs_hyp) == defaultdict 
        assert set(initial_hs_hyp.keys()).issubset(category_set) 

        self.state_set = state_set
        self.current_hyp = initial_hs_hyp

        # state -> label -> frequency 
        self.fmap = defaultdict(dict) 

        # state -> ?is certain of current hypothesis on label? 
        self.s2c_map = {c:False for c in state_set}
        return 

    def sorted_uncertain_states(self): 
        return -1 

    def uncertain_states(self): 
        return -1 

    def update_certainty(self,s2c_map): 
        assert type(s2c_map) == dict 
        assert set(s2c_map.keys()).issubset(self.category_set)

        for k,v in s2c_map.items(): 
            assert type(v) == bool 
            self.s2c_map[k] = v 
        return 

    def set_certain_category(self,c,l):
        assert c in self.category_set
        assert type(l) != type(None) 

        self.s2c_map[c] = True 
        self.current_hyp[c] = l  
        return 

    def max_label_for_category(self,c): 
        assert c in self.category_set

        if c not in self.fmap: 
            return None 

        d = self.fmap[c] 
        if len(d) == 0: return None 

        l2v = [(k,v) for k,v in d.items()] 
        l2v = sorted(l2v,key=lambda x:x[1]) 
        return l2v[-1][0] 

    def add_frequencies_to_category(self,c,f:dict): 
        assert c in self.category_set
        assert type(f) == dict 

        if c not in self.fmap: 
            self.fmap[c] = defaultdict(int) 

        for k,v in f.items(): 
            assert type(v) == int and v >= 0 
            self.fmap[c][k] += v 
        return 

    def update_induction(self): 
        rem_cats = self.category_set - set(self.s2c_map.keys()) 

        for c in rem_cats: 
            q = self.max_label_for_category(c)
            if type(q) != type(None): 
                self.current_hyp[c] = q 
        return 

    def state_induction(self): 
        return deepcopy(self.current_hyp)