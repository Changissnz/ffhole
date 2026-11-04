from xFS_bots.graph_models.extended_dag import * 

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

    def secret_path_map(self,level):  
        return -1 

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
