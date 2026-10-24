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
        ci,ci2,ci3 = [],[],[]
        for p in prg_seq: 
            fq_ = deepcopy(fq) 
            fq_.fs.load_prg(p)

            for _ in range(3): 
                print("",_)
                fq_.exec_one_objective() 
            fq_.display_score() 
            pscores.append(round(fq_.cumulative_path_score,5)) 
            print("--------------------------")

            X = sorted([(k,v) for k,v in fq_.cumulative_inconsistencies_S.items()],\
                key=lambda x:x[1]) 
            ci.append([x[0] for x in X]) 

            X2 = sorted([(k,v) for k,v in fq_.cumulative_inconsistencies_A0.items()],\
                key=lambda x:x[1]) 
            ci2.append([x[0] for x in X2]) 

            X3 = sorted([(k,v) for k,v in fq_.cumulative_inconsistencies_A1.items()],\
                key=lambda x:x[1]) 
            ci3.append([x[0] for x in X3]) 

        assert pscores == [15.13333,9.66667,13.28571], "got {}".format(pscores)

        ## -- subject inconsistencies (answers to agents)
        assert ci[0] == [6, 3, 0, 14, 13, 10, 11, 2, 1, 16, 8, 5, 4, 12, 7, 15, 9]
        assert ci[1] == [2, 0, 12, 3, 15, 13, 11, 10, 7, 14, 6, 9, 5, 4, 1, 8, 16]
        assert ci[2] == [2, 3, 11, 14, 0, 5, 10, 8, 13, 15, 6, 7, 1, 9, 12, 4, 16]

        ## -- agent inconsistencies from subject
        assert ci2[0] == [5, 10, 0]
        assert ci2[1] == [13, 3, 9, 4]
        assert ci2[2] == [5, 3, 7, 15, 8]

        ## -- agent inconsistencies from other agents
        assert ci3[0] == [0, 1, 3, 6, 13, 14, 2, 10, 7, 12, 8, 16, 11, 5, 4, 15, 9]
        assert ci3[1] ==  [0, 6, 10, 2, 3, 13, 14, 12, 15, 7, 4, 8, 16, 1, 5, 9, 11]
        assert ci3[2] == [3, 9, 14, 16, 0, 1, 2, 7, 8, 11, 13, 4, 15, 5, 12, 6, 10]

if __name__ == '__main__':
    unittest.main()