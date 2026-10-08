from automatons.false_incompetency import * 
import unittest

def sample_FIDemander(prg): 
    demand_iterations_seq = [50,30,21,40,10,7]

    D = FIDemander(demand_iterations_seq,prg)
    return D 

"""
py -m tests.test_false_incompetency
"""
# NOTE: runtime on developer's device: approx. 180 seconds. 
class FalseIncompetencyMethods(unittest.TestCase):

    def test__FalseIncompetency__exec_next_demand__case_1(self): 

        prg = prg__LCG(456.55,-100.44,345.55,5454.667)
        G = IncompetentAgentGroupTypeDEGD.generate_instance(7,prg)

        prg2 = prg__LCG(57825.24,523424.335,-5233,90000)
        prg_seq = prg_to_prg__LCG_sequence__v2(prg2,10,[1+2/11,5-4/9])

        scores = [] 
        for i,p in enumerate(prg_seq):
            print("PRNG #{}".format(i))
            D = sample_FIDemander(p)
            F = FalseIncompetency(D,deepcopy(G))
            for _ in range(3): F.exec_next_demand()
            scores.append(F.score())

        assert scores == [-9,8,-5,5,-3,3,7,11,4,2]

if __name__ == '__main__':
    unittest.main()