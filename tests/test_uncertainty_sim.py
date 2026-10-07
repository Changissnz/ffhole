from falses.uncertainty_sim import * 
from morebs2.numerical_generator import prg__LCG
import unittest

"""
py -m tests.test_uncertainty_sim 
"""
# NOTE: runtime on developer's device: approx. 180 seconds. 
class UncertaintySimulatorTypeGGDFunctions(unittest.TestCase):

    def test__UncertaintySimulatorTypeGGD__cmp__case_1(self): 
        prg = prg__LCG(56.55,141.11,-3542.1,5006.66)
        vertex_degree_range = [10,36] 
        edge_connectivity_range = [0.1,0.27] 

        prg2 = prg__LCG(565.33,-252.4,7.5,2002.55) 
        ust = UncertaintySimulatorTypeGGD(prg,vertex_degree_range,edge_connectivity_range)

        V = np.round([ust.cmp(prg2) for _ in range(5)],5)

        assert np.all(V == np.array([0.5,0.56604,0.65438,0.66875,0.6]))
 

if __name__ == '__main__':
    unittest.main()