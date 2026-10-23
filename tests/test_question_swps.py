from falses.question_swps import * 
from xFS_bots.graph_models.graph_gen import * 
import unittest

def sample_QuestionTypeSWPS__V22(prg,\
    proof_simulation_output_space_range=\
        DEFAULT_QUESTION_PROOF_SIMULATION_OUTPUT_SPACE_RATIO_RANGE): 
    is_dsg = False 
    is_realtime_gen = True 
    vertex_degree = 22 
    edge_connectivity = 0.2 
    verbose = False 

    gg = GraphGen(is_dsg,prg,is_realtime_gen,\
        vertex_degree,edge_connectivity,verbose)
    gg.full_run() 
    G = gg.d 
    G = graph_to_one_component(G,prg) 

    answer_set = {0,1,2,3,4,5} 
    node_path_soln_size_range = [2,6] 
    max_num_path_corrections_range = [2,7] 
    start_node_for_paths = 3 

    return QuestionTypeSWPS(G,answer_set,node_path_soln_size_range,\
        max_num_path_corrections_range,prg,start_node_for_paths=None,\
        proof_simulation_output_space_range=proof_simulation_output_space_range) 


"""
py -m tests.test_question_swps 
"""
# NOTE: runtime on developer's device: approx. 180 seconds. 
class QuestionTypeSWPSMethods(unittest.TestCase):

    """
    demonstrates deterministic quality of <QuestionTypeSWPS> 
    """
    def test__QuestionTypeSWPS__next__case_1(self): 
        prg = prg__LCG(53.21,-577.5,1521.54,9767.7)
        Q = sample_QuestionTypeSWPS__V22(prg) 

        # for every iteration, save the necessary PRNG 
        # variables to account for index skews in PRNG output. 
        for _ in range(25):  
            prg0_ = deepcopy(Q.prg) 
            prg0 = deepcopy(Q.prg) 

            Q.choose_node_path_solution() 

            GraphTraversalContextCR.generate_instance(Q.G,\
                DEFAULT_QUESTION_PROOF_SIMULATION_OUTPUT_SPACE_RATIO_RANGE,Q.prg)

            Q.prg,prg0 = prg0,Q.prg 
            X = Q.proof_process(prg0,Q.prg)
            Q.prg = prg0_ 
            assert X[1] == 0 
        return

    def test__QuestionTypeSWPS__next__case_2(self): 

        prg = prg__LCG(5443.21,-277.5,6821.54,15767.7)
        proof_simulation_output_space_range = [0.95,1.0] 
        Q = sample_QuestionTypeSWPS__V22(prg,proof_simulation_output_space_range) 

        prg0 = prg__LCG(63.54,-622.215,55.77,2323.4545) 

        R = [] 
        for _ in range(20): 
            X = Q.proof_process(prg0,Q.prg) 
            R.append((round(X[1],5),X[2])) 

        assert R == [(0, 1.0), (0, 0.5), (0, 0.5), (0, 1.0), (0, 0.0), \
            (0, 1.0), (0, 1.0), (0, 0.5), (0, 0.3333333333333333), \
            (0, 1.0), (0, 1.0), (0, 1.0), (0, 1.0), (0, 0.5), (0, 0.0), \
            (0, 0.0), (0, 1.0), (0, 1.0), (0, 1.0), (0, 1.0)]


if __name__ == '__main__':
    unittest.main()