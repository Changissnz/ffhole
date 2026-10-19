from xFS_bots.graph_models.shortest_paths import * 
from xFS_bots.graph_models.path_induction import * 

from .proof_sim import * 
from morebs2.matrix_methods import is_valid_range
from morebs2.measures import zero_div 

DEFAULT_QUESTION_TYPE_SWPS_NUM_PATHS_PER_NODE = 3 
DEFAULT_QUESTION_TYPE_SWPS_MAX_NUM_PATHS_CORRECTIONS = 5 


"""
Question Type (S)ubjective (W)ith (P)roof (S)imulation. 

Facilitates proof process between a demonstrator and an observer. 
Output determines whether demonstrator or observer answer is accepted. 
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

        self.start_node = None 
        self.preproc(start_node_for_paths) 
        return 

    def preproc(self,start_node_for_paths): 
        if type(start_node_for_paths) == type(None): 
            q = sorted(self.G.keys()) 
            i = int(self.prg()) % len(q) 
            start_node_for_paths = q[i] 
        else: 
            assert start_node_for_paths in self.G 

        self.start_node = start_node_for_paths

        is_bfs = bool(int(self.prg()) % 2) 
        B = BDFSCache(start_node_for_paths,self.G,is_bfs=is_bfs,prg=self.prg,\
            edge_cost_function=lambda u,v:1,\
            num_paths_per_node=DEFAULT_QUESTION_TYPE_SWPS_NUM_PATHS_PER_NODE,\
            max_search_radius=float('inf'),verbose=False)
        B.exec()

        P = PathInduction(start_node_for_paths,B.min_paths,self.prg,num_segment_range=[1,5]) 
        q = P.induce_paths_from_other_references(self.G)

        self.nodepair2paths = defaultdict(list) 
        for k,v in B.min_paths.items(): self.nodepair2paths[(start_node_for_paths,k)] = v 

        for k,v in q.items():
            self.nodepair2paths[k].append(v)  
        return 

    def update_soln(self): 
        return -1 

    def choose_node_path_solution(self): 
        i = modulo_in_range(int(self.prg()),self.node_path_soln_size_range)

        x = sorted(self.G.keys())

        j = int(self.prg()) % len(x) 

        start_node = x.pop(j) 

        q = fetch_paths_from_node_to_nodeset(self.nodepair2paths,start_node,set(x))
        k = prg_seqsort(sorted(q.keys()),self.prg)[:i] 
        paths = [] 
        for k_ in k: paths.extend(q[k_]) 

        return start_node,paths  

    """
    return:
    - [0] path of proof, 
      [1] average difference score with solution paths, 
      [2] ratio of auto-corrected edges over average solution path length 
    """
    def proof_process(self,demonstrator_prng,observer_prng): 

        start_node,paths = self.choose_node_path_solution() 
        P = ProofDifferentialSimulatorTypeACSGT(self.G,start_node,DEFAULT_EDGE_COST_FUNCTION_2,\
            paths,GraphTraversalContextCR(dict()),demonstrator_prng,\
            max_num_path_corrections=DEFAULT_QUESTION_TYPE_SWPS_MAX_NUM_PATHS_CORRECTIONS)

        pf,score = P.exec(observer_prng)

        autocorrect_ratio = zero_div(P.current_ac_units,len(pf) - 1,0)  

        return pf,score,autocorrect_ratio
