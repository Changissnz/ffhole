from xFS_bots.graph_models.extended_dag import * 
from morebs2.numerical_generator import prg_seqsort_ties

DEFAULT_SECRET_DAG_NUM_LAYERS_RANGE = [10,25]
DEFAULT_SECRET_DAG_NUM_NODE_RANGE_PER_LAYER = [5,11] 
DEFAULT_SECRET_DAG_GEN_SCHEME = "constant"
DEFAULT_SECRET_DAG_MULTIPARENT_PR_RANGE = [0.0,0.82]
DEFAULT_SECRET_DAG_INTRALAYER_CONN_RANGE = [0.0,0.55] 
DEFAULT_SECRET_DAG_UNIFORM_DEPTH = True 

"""
maps a NodePath `p` to a state-to-label map M, according to `dag`. 
A `state` is a level of `dag` and a `label` is a node of it. 

Produces M: state -> set of labels. 
"""
def nodepath_to_s2l_map(dag,p:NodePath): 
    D = dag.nodepath_to_level_map(p)
    D = {k:[v] for k,v in D.items()} 

    D2 = invert_map__seqvalue(D)

    if -1 in D2: 
        print("path contains non-existent nodes.")
        assert False 

    return {k:set(v) for k,v in D2.items()} 

"""
sorts vector of label sets for `state` (level) of DAG, in 
ascending order by difference function F, 
    F(other_label_set) = |actual_s2l_map[state] - other_label_set|
"""
def alternative_label_sort(dag:DAGraphContainer,actual_s2l_map,state,prg):

    assert issubclass(type(dag),DAGraphContainer) 

    S = dag.intrasets_of_layer(state)
    S = prg_seqsort_ties(S,prg,vf=lambda x: len(x - actual_s2l_map[state]))
    return S 

"""
generates a state-to-labelset hypothesis map. Generation attempts 
to assign the closest number of correct label sets, as per `correct_ratio`, 
for the states. 

This partitioning of correct and incorrect label sets is dependent on the 
number of single-node layers of the DAG. 

NOTE: single-node DAG layers are strongly advised against for applications 
      such as traversal prediction. 
"""
def generate_s2l_hyp_map(dag,actual_s2l_map,correct_ratio,prg): 

    def alt_labelset(state):  
        S = alternative_label_sort(dag,actual_s2l_map,state,prg) 

        q = S[-1] 
        q_ = q - actual_s2l_map[state]
        if len(q_) > 0: 
            q = q_ 

        q2 = sorted(q) 
        i = int(prg()) % len(q2) 
        return {q2[i]}

    num_correct = ceil(len(dag.l2n_map.items()) * correct_ratio)

    # get set of levels of `dag` that have only one node: 
    # predictions on those levels will always be correct. 
    l1 = set() 
    for k,v in dag.l2n_map.items(): 
        if len(v) < 2: l1 |= {k} 

    l2 = set(dag.l2n_map.keys()) - l1 

    s2l_map = dict()
    for k in l1: 
        s2l_map[k] = deepcopy(dag.l2n_map[k])

    # case: number of levels with single node is @ least correct ratio. 
    if len(l1) >= num_correct: 
        rem = set(dag.l2n_map.keys()) - l1 
    else: 
        l2_ = prg_seqsort(sorted(l2),prg) 
        d = num_correct - len(l1) 

        for i in range(d): 
            k = l2_[i]
            s2l_map[k] = deepcopy(actual_s2l_map[k])
        rem = l2_[d:] 

    if len(rem) == 0: 
        return s2l_map

    rem = prg_seqsort(sorted(rem),prg) 
    for r in rem: 
        s2l_map[r] = alt_labelset(r)
    return s2l_map

"""
Secret Space Type (D)irected (A)cyclic (G)raph. 

Space consists of all paths from root to leaf nodes in 
directed acyclic graph `dag`. Node path `P` is the 
actual secret. 

NOTE: program design is clearly not meant for cryptographically secure 
      application, as is. 
"""
class SecretSpaceTypeDAG: 

    def __init__(self,dag:DAGraphContainer,p:NodePath):
        assert type(dag) == DAGraphContainer
        assert type(p) == NodePath 
        assert does_path_exist(dag.G,p.p) 
        self.dag = dag 
        self.P = p 
        return 

    def secret_path_map(self): 
        return nodepath_to_s2l_map(self.dag,self.P)

    def n_paths_with_node(self,node,num_paths,prg=None): 
        return self.dag.n_paths_with_node(node,num_paths,False,prg)

    def n_paths_with_nodeset(self,nodeset,num_paths,prg=None): 
        return self.dag.n_paths_with_nodeset(nodeset,num_paths,False,prg)

    """
    generates a standard instance of <SecretSpaceTypeDAG>, using the 
    default values provided at the top. 
    """
    @staticmethod
    def generate_std_instance(prg): 

        D = SecretSpaceTypeDAG.generate_std_DAG(prg,True) 

        # choose a path 
        #   first, choose a leaf node 
        i = int(prg()) % len(D.leaf_nodes)
        n = D.leaf_nodes[i]
        P = D.n_paths_with_node(n,1,False,prg)[0]
        
        dag = D.to_DAGraph() 
        return SecretSpaceTypeDAG(dag,P) 

    @staticmethod 
    def generate_std_DAG(prg,output_is_generator:bool=False,\
        num_layers_range=DEFAULT_SECRET_DAG_NUM_LAYERS_RANGE,\
        num_nodes_per_layer_range=DEFAULT_SECRET_DAG_NUM_NODE_RANGE_PER_LAYER,\
        multiparent_pr_range=DEFAULT_SECRET_DAG_MULTIPARENT_PR_RANGE,\
        intralayer_conn_range=DEFAULT_SECRET_DAG_INTRALAYER_CONN_RANGE,\
        uniform_depth=DEFAULT_SECRET_DAG_UNIFORM_DEPTH):

        num_layers = modulo_in_range(int(prg()),num_layers_range)

        D = DAGraphGen(num_nodes_per_layer_range,DEFAULT_SECRET_DAG_GEN_SCHEME,\
        multiparent_pr_range,intralayer_conn_range,\
        prg,uniform_depth)

        for _ in range(num_layers): 
            next(D)

        D.permute_nodes()  
        if output_is_generator: 
            return D 
        return D.to_DAGraph() 
