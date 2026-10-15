from falses.proof_sim import * 
from morebs2.numerical_generator import prg__LCG
from xFS_bots.graph_models.graph_gen import * 
from xFS_bots.graph_models.shortest_paths import * 
from xFS_bots.graph_models.bfs import * 
import unittest

def graph_and_paths_case_BASE(prg):
    G = defaultdict(set,{0:{1,2},\
        1:{3},\
        2:{3,4}})  

    B = BFSCache(0,G)
    B.exec() 
    B.store_minpaths(num_paths=1000)
    node_path_solution_seq = [x.invert() for x in B.min_paths[3]]

    return G,node_path_solution_seq

def graph_and_paths_case_COMPLEX0(prg): 

    is_dsg = False 
    is_realtime_gen = True 
    vertex_degree = 30 
    edge_connectivity = 0.2 
    verbose = False 

    gg = GraphGen(is_dsg,prg,is_realtime_gen,\
        vertex_degree,edge_connectivity,verbose)
    gg.full_run() 
    G = gg.d 

    G = graph_to_one_component(G,prg) 

    start_node = 5 

    bd = BDFSCache(start_node,G,is_bfs=True,prg=prg,\
        edge_cost_function=lambda u,v:1,num_paths_per_node=1,\
        max_search_radius=float('inf'),verbose=False)
    bd.exec() 

    P,components = BDFSCache.BFS_full(G,nodeset=None,return_type="paths",prg=prg,max_search_radius=float('inf'),\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,verbose=False)

    start_node = 21 
    edge_cost_function = DEFAULT_EDGE_COST_FUNCTION_2
    node_path_solution_seq = [P[(start_node,28)],P[(start_node,5)],P[(start_node,15)]]

    return G,node_path_solution_seq

"""
py -m tests.test_proof_sim 
"""
# NOTE: runtime on developer's device: approx. 180 seconds. 
class ProofDifferentialSimulatorTypeXMethods(unittest.TestCase):

    def test__ProofDifferentialSimulatorTypeSGT__next__case_1(self): 
        prg = prg__LCG(53.21,-577.5,1521.54,9767.7)
        G,node_path_solution_seq = graph_and_paths_case_BASE(prg) 
        start_node = 0  
        edge_cost_function = DEFAULT_EDGE_COST_FUNCTION_2

        psim = ProofDifferentialSimulatorTypeSGT(G,start_node,edge_cost_function,node_path_solution_seq)

        q = [] 
        for _ in range(15): 
            x = psim.exec(prg) 
            q.append(x[1])

        assert q == [0, 0, 0, 5.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5.5, 0]
        return 

    def test__ProofDifferentialSimulatorTypeSGT__next__case_2(self): 
        prg = prg__LCG(53.21,-577.5,1521.54,9767.7)
        G,node_path_solution_seq = graph_and_paths_case_COMPLEX0(prg) 
        start_node = 21 
        edge_cost_function = DEFAULT_EDGE_COST_FUNCTION_2

        psim = ProofDifferentialSimulatorTypeSGT(G,start_node,edge_cost_function,node_path_solution_seq)

        q = [] 
        for _ in range(15): 
            x = psim.exec(prg) 
            q.append(round(x[1],5)) 

        assert q == [0,0,5.66667,7.66667,8.0,7.0,7.66667,7.66667,\
            10.0,9.33333,7.66667,8.0,8.0,5.66667,7.0]

if __name__ == '__main__':
    unittest.main()