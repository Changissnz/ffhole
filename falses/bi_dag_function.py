from .dag_secret import * 
from seqbuild.intigers.mod_prng import * 

"""
(D)irected (A)cyclic (G)raph Traversal Function Type (H)idden (S)tate (D)irected. 

Uses a reference directed acyclic graph `dag` and a PRNG of type class<NoiseAddedIterableContainer> 
from project<seqbuild> for decision-making. 

A Bi-DAG operator, when given a `hidden_state_map` corresponding to `dag`, calculates the next 
node n' XOR NULL from n; n,n' in `dag2`, another directed acyclic graph.
"""
class DAGTraversalFunctionTypeHSD: 

    def __init__(self,dag:DAGraphContainer,prng_struct:NoiseAddedIterableContainer):
        assert type(dag) == DAGraphContainer
        assert type(prng_struct) == NoiseAddedIterableContainer

        self.dag = dag 
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
            prt = prg_uniform_partition_sequence(l_nodeset,len(C),prg)

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

"""
State Induction Type (M)ost (F)requent (U)nless (C)ertain. 
"""
class StateInductionTypeMFUC: 

    def __init__(self): 
        return -1 
