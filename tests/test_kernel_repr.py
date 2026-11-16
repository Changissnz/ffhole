from falses.kernel_repr import * 
import unittest


"""
py -m tests.test_kernel_repr 
"""
class KernelReprTypeDCCMethods(unittest.TestCase):

    def test__KernelReprTypeDCC__constituent_chains__case_1(self): 
        S = [4,5,10,23,211,56,34] 

        K = KernelReprTypeDCC(S)

        c5 = K.constituent_chains(5) 


        K.add_element(73,{5,10,211},identity_form_function()) 
        K.add_element(49,{56,34,4},identity_form_function()) 
        K.add_element(17,{73,49,4,211},identity_form_function()) 

        c73 = K.constituent_chains(73) 
        d73 = K.constituent_chains_to_degree(c73) 

        assert c73 == [[[{5}]], [[{10}]], [[{211}]]]
        assert d73 == 1

        c17 = K.constituent_chains(17) 
        d17 = K.constituent_chains_to_degree(c17) 

        assert c17 == [[[{4}]], [[{49}], [{56, 34, 4}]], [[{73}], [{10, 211, 5}]], [[{211}]]]
        assert d17 == 2 

        K.add_element(71,{17,49,34,10},identity_form_function()) 
        K.add_element(712,{71,17,49,73,211},identity_form_function()) 

        c712 = K.constituent_chains(712) 
        d712 = K.constituent_chains_to_degree(c712) 

        assert c712 == [[[{17}], [{73, 211, 4, 49}], [{56, 34, 4}, {10, 211, 5}]], \
            [[{49}], [{56, 34, 4}]], \
            [[{71}], [{17, 34, 10, 49}], \
            [{73, 211, 4, 49}, {56, 34, 4}], [{56, 34, 4}, {10, 211, 5}]], [[{73}], [{10, 211, 5}]], \
            [[{211}]]]
        assert d712 == 4 
        return  

    def test__KernelReprTypeDCC__process_element__case_1(self):

        S = [4,5,10,23,211,56,34] 
        K = KernelReprTypeDCC(S)
        c5 = K.constituent_chains(5) 

        K.add_element(73,{5,10,211},identity_form_function()) 
        K.add_element(49,{56,34,4},identity_form_function()) 
        K.add_element(17,{73,49,4,211},identity_form_function()) 
        K.add_element(71,{17,49,34,10},identity_form_function()) 
        K.add_element(712,{71,17,49,73,211},identity_form_function()) 

        c712 = K.constituent_chains(712) 
        d712 = K.constituent_chains_to_degree(c712) 

        X = K.process_element(712) 
        assert X == [[{73, 211, 4, 49}], [{4}, {56, 34, 4}, {10, 211, 5}, {211}], \
            [{4}, {34}, {56}, {5}, {10}, {211}], \
            [{56, 34, 4}], [{4}, {34}, {56}], \
            [{17, 34, 10, 49}], \
            [{10}, {73, 211, 4, 49}, {34}, {56, 34, 4}], \
            [{4}, {56, 34, 4}, {10, 211, 5}, {211}, {4}, {34}, {56}], \
            [{4}, {34}, {56}, {5}, {10}, {211}], \
            [{10, 211, 5}], \
            [{5}, {10}, {211}], \
            [{211}]]

if __name__ == '__main__':
    unittest.main()