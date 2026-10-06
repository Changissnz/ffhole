from falses.incon_ccde import * 
from morebs2.numerical_generator import prg__LCG,prg__constant 

from automatons.graph_comp_ext import * 
from morebs2.numerical_generator import prg__LCG
import unittest


"""
py -m tests.test_incon_ccde 
"""
# NOTE: runtime on developer's device: approx. 180 seconds. 
class InconsistentFunctionTypeCCDEFunctions(unittest.TestCase):

    def test__InconsistentFunctionTypeCCDE__iterate__case_1(self): 

        l = [7,3,4,5]
        F = cumulative_modulo_boolean_function(sum(l),{5,7,11}) 
        G = InconsistentFunctionTypeCCDE(l,F,lambda x: not bool(x)) 

        prg = prg__LCG(0,3,2.55,10.11) 
        prg = prg__constant(0) 

        Q = G.demo_iterate(20,prg) 
        Q2 = G.exec_iterate() 

        assert np.all(Q == Q2)

        prg = prg__LCG(0,3,2.55,10.11) 
        Q3 = G.demo_iterate(20,prg) 
        Q4 = G.exec_iterate() 

        X = np.where(np.array(Q3) != np.array(Q4))
        assert np.where(X[0] == np.array([ 2,  4,  8,  9, 11, 12, 13, 14, 15, 17, 18]))

    def test__InconsistentFunctionTypeCCDE__iterate__case_2(self):

        k = 5 
        prg = prg__LCG(56,-431.77,21.14,789.55) 
        F = InconsistentFunctionTypeCCDE.generate_instance_v2(k,prg)

        V = F.demo_iterate(20,prg) 
        V2 = F.exec_iterate() 

        assert np.all(np.where(V != V2)[0] == np.array([ 5,  9, 10, 12, 14, 15, 18]))

if __name__ == '__main__':
    unittest.main()