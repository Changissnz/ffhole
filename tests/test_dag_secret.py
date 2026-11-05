from falses.dag_secret import * 
from morebs2.numerical_generator import prg__LCG
from morebs2.matrix_methods import vector_to_string
import unittest

###

"""
py -m tests.test_dag_secret 
""" 
class SecretSpaceTypeDAGMethods(unittest.TestCase):

    """
    tests uniqueness of calculated paths to node 10 in sample 
    <SecretSpaceTypeDAG>. 

    tests path differences between two different <SecretSpaceTypeDAG>s. 
    """
    def test__SecretSpaceTypeDAG__n_paths_with_node__case_1(self): 

        prg = prg__LCG(735.78,-1414.141,55.62,7143.61)

        # subcase 1 
        S = SecretSpaceTypeDAG.generate_std_instance(prg) 

        V = set() 
        for _ in range(20): 
            p = S.n_paths_with_node(10,1,prg)[0]
            ps = vector_to_string(p.p)
            V |= {ps} 
        assert len(V) == 20 

        # subcase 2 
        S2 = SecretSpaceTypeDAG.generate_std_instance(prg) 

        V2 = set() 
        for _ in range(20): 
            p = S2.n_paths_with_node(10,1,prg)[0]
            ps = vector_to_string(p.p)
            V2 |= {ps} 
        assert len(V2) == 20, "got {}".format(len(V2))

        d = (V - V2) | (V2 - V)
        assert len(d) == 40, "got {}".format(len(d)) 

if __name__ == '__main__':
    unittest.main()