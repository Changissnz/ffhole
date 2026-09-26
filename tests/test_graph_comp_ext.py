from automatons.graph_comp_ext import * 
from morebs2.numerical_generator import prg__LCG
import unittest


"""
py -m tests.test_graph_comp_ext 
"""
# NOTE: runtime on developer's device: approx. 180 seconds. 
class GraphCompExtFunctions(unittest.TestCase):

    def test__prg_choose_subrange_for_n_elements__case_1(self): 

        # subcase 1 
        numbers = [5,6,15,55,5.1,6,6,6,6,1,2] 
        n = 5 
        prg = prg__LCG(56.4,-13.2,43.5,432.1)

        S = prg_choose_subrange_for_n_elements(numbers,n,prg,\
            starting_index = None,default_zero_distance=5.0,\
            default_zero_diameter=1.0)

        assert frequency_of_range_for_vector(np.array(numbers),S) == 7

        # subcases 2-6 
        numbers2 = [5,6,15,55,5.1,6,6,6,6,1,2,15,15,10] 

        S2 = prg_choose_subrange_for_n_elements(numbers2,n,prg,\
            starting_index = None,default_zero_distance=5.0,\
            default_zero_diameter=1.0)

        S3 = prg_choose_subrange_for_n_elements(numbers2,n,prg,\
            starting_index = None,default_zero_distance=5.0,\
            default_zero_diameter=1.0)

        S4 = prg_choose_subrange_for_n_elements(numbers2,n,prg,\
            starting_index = None,default_zero_distance=5.0,\
            default_zero_diameter=1.0)

        S5 = prg_choose_subrange_for_n_elements(numbers2,n,prg,\
            starting_index = None,default_zero_distance=5.0,\
            default_zero_diameter=1.0)

        S6 = prg_choose_subrange_for_n_elements(numbers2,n,prg,\
            starting_index = None,default_zero_distance=5.0,\
            default_zero_diameter=1.0)

        assert frequency_of_range_for_vector(np.array(numbers2),S2) == 4
        assert frequency_of_range_for_vector(np.array(numbers2),S3) == 5
        assert frequency_of_range_for_vector(np.array(numbers2),S4) == 4
        assert frequency_of_range_for_vector(np.array(numbers2),S5) == 5
        assert frequency_of_range_for_vector(np.array(numbers2),S6) == 4

    def test__prg_choose_subrange_for_n_elements__case_2(self): 

        numbers = [5,6,15,55,5.1,6,6,6,645,67,321,455,653,1,2] 

        # subcase 1 
        n = 0  
        prg = prg__LCG(56.4,-13.2,43.5,432.1)

        S = prg_choose_subrange_for_n_elements(numbers,n,prg,\
            starting_index = None,default_zero_distance=5.0,\
            default_zero_diameter=1.0)

        assert frequency_of_range_for_vector(np.array(numbers),S) == 0 

        # subcase 2 
        n2 = len(numbers) 
        S2 = prg_choose_subrange_for_n_elements(numbers,n2,prg,\
            starting_index = None,default_zero_distance=5.0,\
            default_zero_diameter=1.0)

        assert frequency_of_range_for_vector(np.array(numbers),S2) == n2  

if __name__ == '__main__':
    unittest.main()