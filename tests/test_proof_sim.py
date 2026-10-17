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

def graph_and_paths_case_BASE1(prg): 

    is_dsg = False 
    is_realtime_gen = True 
    vertex_degree = 12 
    edge_connectivity = 0.3 
    verbose = False 

    gg = GraphGen(is_dsg,prg,is_realtime_gen,\
        vertex_degree,edge_connectivity,verbose)
    gg.full_run() 
    G = gg.d 
    G = graph_to_one_component(G,prg) 

    path = NodePath.preload([2,10,9,4,3,0],[1,1,1,1,1])
    node_path_solution_seq = [path.invert()] 

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

def graph_and_paths_case_COMPLEX1(prg):

    is_dsg = False 
    prg = prg__LCG(53.21,-577.5,1521.54,9767.7)
    is_realtime_gen = True 
    vertex_degree = 22 
    edge_connectivity = 0.1 
    verbose = False 

    gg = GraphGen(is_dsg,prg,is_realtime_gen,\
        vertex_degree,edge_connectivity,verbose)
    gg.full_run() 
    G = gg.d 

    G = graph_to_one_component(G,prg) 

    B = BFSCache(0,G)
    B.exec() 
    B.store_minpaths(num_paths=1000)

    node_path_solution_seq = [x.invert() for x in B.min_paths[2]]

    return G,node_path_solution_seq


def GraphTraversalContextCR_case_BASE10(): 
    D = {0: {3: 3, 4: 3, 5: 3, 11: 3},\
        1: {3: 4, 4: 4, 7: 4},\
        2: {4: 8, 8: 8, 10: 8, 11: 8},\
        3: {0: 4, 1: 4, 4: 4, 6: 1, 9: 1, 10: 1},\
        4: {0: 9, 1: 9, 2: 2, 3: 9, 5: 2, 7: 2, 9: 9},\
        5: {0: 4, 4: 4},\
        6: {3: 3},\
        7: {1: 4, 4: 4, 8: 8},\
        8: {2: 2, 7: 7},\
        9: {3: 10, 4: 10, 10: 10}, \
        10: {2: 2, 3: 2, 9: 2},\
        11: {0: 0, 2: 2}} 

    return GraphTraversalContextCR(D) 

# NOTE: identical to BASE10, except for [3] 
def GraphTraversalContextCR_case_BASE11(): 
    D = {0: {3: 3, 4: 3, 5: 3, 11: 3},\
        1: {3: 4, 4: 4, 7: 4},\
        2: {4: 8, 8: 8, 10: 8, 11: 8},\
        3: {0: 4, 1: 4, 4: 4, 6: 4, 9: 4, 10: 4},\
        4: {0: 9, 1: 9, 2: 2, 3: 9, 5: 2, 7: 2, 9: 9},\
        5: {0: 4, 4: 4},\
        6: {3: 3},\
        7: {1: 4, 4: 4, 8: 8},\
        8: {2: 2, 7: 7},\
        9: {3: 10, 4: 10, 10: 10},\
        10: {2: 2, 3: 2, 9: 2},\
        11: {0: 0, 2: 2}} 

    return GraphTraversalContextCR(D) 

"""
py -m tests.test_proof_sim 
"""
# NOTE: runtime on developer's device: approx. 180 seconds. 
class ProofDifferentialSimulatorTypeXMethods(unittest.TestCase):

    """
    small graph: external party proof results in correct solution most of the time. 
    """
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

    """
    more complex graph: external party proof does not result in correct solution most of the time. 
    """
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

    """
    correct answer 56/200 times 
    """
    def test__ProofDifferentialSimulatorTypeCSGT__next__case_1(self): 
        prg = prg__LCG(53.21,-577.5,1521.54,9767.7)
        G,node_path_solution_seq = graph_and_paths_case_BASE1(prg)
        start_node = 0 
        edge_cost_function = DEFAULT_EDGE_COST_FUNCTION_2
        gtc_cr = GraphTraversalContextCR_case_BASE10()
        
        psim = ProofDifferentialSimulatorTypeCSGT(G,start_node,edge_cost_function,node_path_solution_seq,gtc_cr) 

        count = defaultdict(int)
        for _ in range(200): 
            q = psim.exec(prg) 
            count[q[1]] += 1 

        assert count == defaultdict(int, {0: 56, 6.0: 69, 11.0: 46, 9.0: 29})

    """
    correct answer 133/200 times 
    """
    def test__ProofDifferentialSimulatorTypeCSGT__next__case_2(self): 
        prg = prg__LCG(53.21,-577.5,1521.54,9767.7)
        G,node_path_solution_seq = graph_and_paths_case_BASE1(prg)
        start_node = 0 
        edge_cost_function = DEFAULT_EDGE_COST_FUNCTION_2
        gtc_cr = GraphTraversalContextCR_case_BASE11()
        
        psim = ProofDifferentialSimulatorTypeCSGT(G,start_node,edge_cost_function,node_path_solution_seq,gtc_cr) 

        count = defaultdict(int)
        for _ in range(200): 
            q = psim.exec(prg) 
            count[q[1]] += 1 

        assert count == defaultdict(int, {0: 133, 9.0: 67})

    def test__ProofDifferentialSimulatorTypeACSGT__next__case_1(self): 
        
        prg = prg__LCG(53.21,-577.5,1521.54,9767.7)
        G,node_path_solution_seq = graph_and_paths_case_COMPLEX1(prg)
        gtc_cr = GraphTraversalContextCR(dict())

        start_node = 0  
        edge_cost_function = DEFAULT_EDGE_COST_FUNCTION_2

        psim = ProofDifferentialSimulatorTypeACSGT(G,start_node,edge_cost_function,node_path_solution_seq,gtc_cr,prg) 

        count = defaultdict(int)
        for _ in range(200): 
            q = psim.exec(prg) 
            count[q[1]] += 1 

        assert len(count) == 1 and {0} == set(count.keys())

        assert round(psim.cumulative_ac_sum,5) == 214.04794 
        assert psim.cumulative_ac_units == 482 

    def test__ProofDifferentialSimulatorTypeACSGT__next__case_2(self): 

        prg = prg__LCG(53.21,-577.5,1521.54,9767.7)

        G,node_path_solution_seq = graph_and_paths_case_COMPLEX1(prg)

        start_node = 0  
        edge_cost_function = DEFAULT_EDGE_COST_FUNCTION_2

        ##### case 1: context w/ 25-30% choice 
        gtc_cr = GraphTraversalContextCR.generate_instance(G,[0.25,0.30],prg) #[0.02,0.2],prg) 

        psim = ProofDifferentialSimulatorTypeACSGT(G,start_node,edge_cost_function,node_path_solution_seq,gtc_cr,prg) 
        count = defaultdict(int)
        for _ in range(200): 
            q = psim.exec(prg) 
            count[q[1]] += 1 

        assert count == defaultdict(int, {8.5: 53, 10.25: 47, 0: 89, 12.375: 11}), "got {}".format(count)

        ##### case 2: context w/ 60-70% choice 
        psim.prng_update_context([0.6,0.7],prg) 
        count = defaultdict(int)
        for _ in range(200): 
            q = psim.exec(prg) 
            count[q[1]] += 1 

        assert count == defaultdict(int, {0: 189, 8.75: 3, 8.5: 3, 10.25: 5}), "got {}".format(count)
        return 

if __name__ == '__main__':
    unittest.main()