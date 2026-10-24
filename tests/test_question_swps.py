from .sample_cases import * 
import unittest

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
        L = [] 
        for _ in range(250):  
            #prg0_ = deepcopy(Q.prg) 
            prg0 = deepcopy(Q.prg) 

            Q.choose_node_path_solution() 

            GraphTraversalContextCR.generate_instance(Q.G,\
                DEFAULT_QUESTION_PROOF_SIMULATION_OUTPUT_SPACE_RATIO_RANGE,Q.prg)
            Q.prg,prg0 = prg0,Q.prg 
            X = Q.proof_process(prg0,Q.prg)
            L.append(round(X[1],5)) 

        # NOTE: not entirely identical b/t the two PRNGs due to skew  
        #       from internal PRNG calls in 
        #       method<ProofDifferentialSimulatorTypeACSGT.external_agent_path>. 
        assert L == [0, 0, 0, 0, 4.5, 0, 0, 6.0, 4.0, 6.5, 5.0, 0, 6.0, \
            0, 5.0, 4.8, 0, 8.0, 0, 0, 9.0, 3.0, 0, 6.66667, 5.0, 0, 4.5, \
            4.66667, 12.33333, 0, 0, 7.0, 0, 0, 0, 0, 0, 7.83333, 7.5, 0, \
            0, 0, 7.0, 5.0, 0, 0, 0, 0, 4.0, 0, 0, 6.0, 4.66667, 5.0, 7.4, \
            0, 4.5, 0, 0, 3.4, 0, 0, 4.0, 0, 4.66667, 0, 9.8, 0, 6.75, 10.0, \
            0, 0, 4.66667, 0, 0, 4.66667, 5.0, 6.0, 0, 5.0, 0, 0, 4.25, 0, \
            0, 0, 8.0, 4.66667, 4.5, 4.66667, 4.0, 0, 4.0, 4.0, 4.0, 0, 0, \
            0, 0, 0, 0, 0, 0, 0, 0, 0, 4.66667, 4.8, 2.66667, 0, 0, 0, 5.75, \
            4.0, 0, 8.0, 4.0, 4.0, 6.25, 6.0, 4.0, 0, 5.0, 0, 0, 6.5, 6.0, \
            5.75, 0, 0, 4.5, 5.5, 0, 5.8, 0, 0, 4.0, 0, 0, 0, 6.0, 0, 0, \
            4.5, 0, 0, 3.5, 7.0, 6.66667, 0, 0, 0, 0, 10.0, 0, 4.66667, 0, \
            0, 0, 7.0, 0, 4.0, 8.0, 0, 9.875, 4.0, 0, 5.0, 11.86667, 0, 0, \
            0, 0, 0, 0, 0, 4.0, 0, 4.0, 4.66667, 8.0, 8.0, 13.13333, 0, 9.2, \
            0, 7.0, 4.5, 6.33333, 0, 0, 4.5, 6.75, 0, 0, 0, 0, 0, 0, 6.25, \
            3.5, 0, 0, 5.0, 4.66667, 6.0, 3.4, 4.25, 0, 0, 8.0, 0, 0, 4.0, \
            0, 7.0, 3.4, 8.0, 10.75, 4.25, 6.0, 0, 6.66667, 4.66667, 5.0, \
            2.5, 6.0, 0, 5.2, 0, 0, 4.5, 4.5, 11.16667, 7.0, 0, 0, 0, 12.7, \
            6.33333, 0, 0, 5.5, 0, 5.0, 7.0, 0, 0, 0, 0]
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