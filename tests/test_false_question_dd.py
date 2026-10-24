from automatons.false_question_dd import * 
from morebs2.numerical_generator import prg_to_prg__LCG_sequence__v2
import unittest

###

"""
py -m tests.test_false_question_dd
""" 
class FalseQuestionTypeDDMethods(unittest.TestCase):

    """
    demonstrates variance in performance of <FQSubjectTypeDD> 
    over different PRNGs. 
    """ 
    def test__FalseQuestionTypeDD__exec_one_objective__case_1(self): 
        num_swarm_agents = 17
        num_answers = 11 
        prg = prg__LCG(873.2,-633.63,68.66,97166.6) 

        fq = FalseQuestionTypeDD.generate_instance(num_swarm_agents,num_answers,prg,verbose=False) 

        prg_seq = prg_to_prg__LCG_sequence__v2(prg,3,[2+7/9,6-1/9]) 

        fq_ = None 
        pscores = [] 
        for p in prg_seq: 
            fq_ = deepcopy(fq) 
            fq_.fs.load_prg(p)

            for _ in range(3): 
                print("",_)
                fq_.exec_one_objective() 
            fq_.display_score() 
            pscores.append(round(fq_.cumulative_path_score,5)) 
            print("--------------------------")

        assert pscores == [15.13333,9.66667,13.28571], "got {}".format(pscores)

if __name__ == '__main__':
    unittest.main()