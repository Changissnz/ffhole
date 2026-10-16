
DEFAULT_QUESTION_TYPE_SWPS_NUM_PATHS_PER_NODE = 3 

"""
Question Type (S)ubjective (W)ith (P)roof (S)imulation. 

Operates 
"""
class QuestionTypeSWPS: 

    def __init__(self,G,answer_set,node_path_soln_size_range,max_num_path_corrections_range,prg,start_node_for_paths=None):   
        assert type(G) == defaultdict
        assert type(answer_set) == set 
        assert is_valid_range(node_path_soln_size_range,True,False) and node_path_soln_size_range[0] > 0 
        assert is_valid_range(max_num_path_corrections_range,True,False) and max_num_path_corrections_range[0] > 0 
        assert type(prg) in {MethodType,FunctionType}

        self.G = G 
        self.answer_set = answer_set
        self.node_path_soln_size_range = node_path_soln_size_range
        self.max_num_path_corrections_range = max_num_path_corrections_range
        self.prg = prg  
        self.preproc(start_node_for_paths) 
        return 

    def preproc(self,start_node_for_paths): 
        if type(start_node_for_paths) == type(None): 
            q = sorted(G.keys()) 
            i = int(self.prg()) % len(q) 
            start_node_for_paths = q[i] 
        else: 
            assert start_node_for_paths in self.G 

        is_bfs = bool(int(self.prg()) % 2) 
        B = BDFSCache(start_node_for_paths,G,is_bfs=is_bfs,prg=self.prg,\
            edge_cost_function=lambda u,v:1,\
            num_paths_per_node=DEFAULT_QUESTION_TYPE_SWPS_NUM_PATHS_PER_NODE,\
            max_search_radius=float('inf'),verbose=False)
        B.exec()

        P = PathInduction(start_node_for_paths,B.min_paths,prg,num_segment_range=[1,5]) 
        q = P.induce_paths_from_other_references(G)

        self.nodepair2paths = defaultdict(list) 
        for k,v in B.min_paths: self.nodepair2paths[(start_node_for_paths,k)] = v 

        for k,v in q.items(): 
            self.nodepair2paths[k].append(v) 
        return 

    def update_soln(self): 
        return -1 

    def proof_process(self,demonstrator_ans,observer_ans): 
        return -1 

