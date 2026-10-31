from xFS_bots.graph_models.dag_gen import * 

DEFAULT_SECRET_DAG_NUM_LAYERS_RANGE = [10,25]
DEFAULT_SECRET_DAG_NUM_NODE_RANGE_PER_LAYER = [5,11] 
DEFAULT_SECRET_DAG_GEN_SCHEME = "constant"
DEFAULT_SECRET_DAG_MULTIPARENT_PR_RANGE = [0.0,0.82]
DEFAULT_SECRET_DAG_INTRALAYER_CONN_RANGE = [0.0,0.55] 
DEFAULT_SECRET_DAG_UNIFORM_DEPTH = True 

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

    """
    generates a standard instance of <SecretSpaceTypeDAG>, using the 
    default values provided at the top. 
    """
    @staticmethod
    def generate_std_instance(prg): 

        num_layers = modulo_in_range(int(prg()),DEFAULT_SECRET_DAG_NUM_LAYERS_RANGE)

        D = DAGraphGen(DEFAULT_SECRET_DAG_NUM_NODE_RANGE_PER_LAYER,DEFAULT_SECRET_DAG_GEN_SCHEME,\
        DEFAULT_SECRET_DAG_MULTIPARENT_PR_RANGE,DEFAULT_SECRET_DAG_INTRALAYER_CONN_RANGE,\
        prg,DEFAULT_SECRET_DAG_UNIFORM_DEPTH)

        for _ in range(num_layers): 
            next(D) 

        D.permute_nodes() 
        
        # choose a path 
        #   first, choose a leaf node 
        i = int(prg()) % len(D.leaf_nodes)
        n = D.leaf_nodes[i]
        P = D.n_paths_with_node(n,1,prg)[0]
        
        dag = D.to_DAGraph() 
        return SecretSpaceTypeDAG(dag,P) 