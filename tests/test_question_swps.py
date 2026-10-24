from .sample_cases import * 
import unittest

"""
py -m tests.test_question_swps 
"""
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
        assert L == [0, 0, 5.33333, 8.0, 5.66667, 6.5, 0, 7.5, 0, 6.5, \
            5.0, 0, 7.0, 4.0, 0, 0, 8.0, 10.0, 3.5, 3.4, 5.66667, \
            0, 0, 0, 0, 5.0, 8.0, 0, 0, 4.8, 7.0, 0, 0, 3.5, 0, 0, \
            0, 5.66667, 0, 0, 0, 6.25, 0, 5.8, 11.0, 6.8, 4.66667, \
            5.0, 0, 5.33333, 0, 0, 5.5, 0, 0, 7.53846, 4.0, 0, 5.5, \
            6.75, 6.8, 0, 0, 5.0, 0, 5.4, 0, 5.6, 4.66667, 6.5, 0, 8.0, \
            5.0, 4.8, 7.0, 0, 8.75, 0, 0, 8.0, 0, 0, 4.75, 0, 0, 0, \
            6.75, 3.0, 0, 5.0, 0, 0, 0, 8.83333, 0, 0, 7.33333, 0, 7.5, \
            0, 7.2, 4.0, 3.4, 0, 0, 0, 6.4, 0, 4.5, 10.0, 0, 0, 0, 5.0, \
            7.2, 0, 0, 0, 4.0, 5.0, 0, 0, 8.0, 0, 0, 0, 6.33333, 5.6, 4.75, \
            6.0, 8.0, 0, 4.33333, 0, 0, 0, 0, 10.0, 0, 0, 4.75, 0, 0, 5.5, \
            3.5, 0, 6.33333, 0, 4.4, 5.0, 6.0, 0, 0, 3.4, 0, 5.75, 5.75, \
            0, 0, 0, 9.0, 0, 0, 3.5, 0, 0, 0, 5.33333, 0, 0, 5.66667, 0, \
            6.5, 9.0, 0, 4.5, 0, 0, 2.0, 6.66667, 9.4, 0, 4.0, 0, 0, 0, \
            0, 0, 3.0, 0, 0, 0, 8.33333, 3.66667, 4.0, 0, 0, 0, 6.5, 0, \
            5.0, 0, 0, 0, 0, 6.0, 0, 0, 3.5, 5.8, 6.0, 10.0, 0, 0, 0, \
            4.66667, 0, 5.0, 0, 0, 0, 3.0, 4.4, 0, 2.5, 0, 8.0, 0, 6.75, \
            4.5, 10.17647, 0, 0, 0, 3.4, 0, 11.0, 0, 0, 0, 6.66667, 4.5, 0, \
            8.0, 0, 6.0, 0, 0, 0, 0], "got {}".format(L)
        return

    # NOTE: tests for 0 path difference, given complete context. 
    def test__QuestionTypeSWPS__next__case_2(self): 

        prg = prg__LCG(5443.21,-277.5,6821.54,15767.7)
        proof_simulation_output_space_range = [1.0,1.0] 
        Q = sample_QuestionTypeSWPS__V22(prg,proof_simulation_output_space_range) 

        prg0 = prg__LCG(63.54,-622.215,55.77,2323.4545) 

        R = [] 
        for _ in range(200): 
            X = Q.proof_process(prg0,Q.prg) 
            R.append((round(X[1],5),X[2])) 

        c = len([r for r in R if r[0] != 0]) 
        assert c == 0, "GOT {}".format(c) 


if __name__ == '__main__':
    unittest.main()