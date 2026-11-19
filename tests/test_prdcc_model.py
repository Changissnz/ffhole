from falses.prdcc_model import * 
from morebs2.numerical_generator import prg__LCG 
import unittest

def sample_PRDCCFunctionGen_R311(form_type): 
    label_set = {4,5,6,12,31,112,67,823} 
    prg = prg__LCG(634.52,-2352.2,563.44,13449.65) 
    pfg = PRDCCFunctionGen(label_set,prg,form_type)
    return pfg 

"""
py -m tests.test_prdcc_model
"""
class PRDCCFunctionGenMethods(unittest.TestCase):

    def test__PRDCCFunctionGen__add_element__case_1(self): 

        pfg = sample_PRDCCFunctionGen_R311("P") 

        e0_literal = {5,6}
        e0_idn = {pfg.base_to_int_idn(i) for i in e0_literal}

        pfg.add_element(e0_idn) 

        assert set(pfg.i2f_map.keys()) == {i for i in range(8 + 1)} 

        assert pfg.element_to_int_label(e0_idn) == 8 

        e1_literal = {5,6,12,31}
        e1_idn = {pfg.base_to_int_idn(i) for i in e1_literal}

        pfg.add_element(e1_idn)  
        assert pfg.element_to_int_label(e1_idn) == 9 

        # try adding a phony element, 
        e2 = {5,6,112,235423}
        try: 
            pfg.add_element(e2) 
            assert False 
        except: 
            assert True 


    def test__PRDCCFunctionGen__function_consistency__case_1(self): 
        pfg = sample_PRDCCFunctionGen_R311("G")  

        e0_literal = {5,6}
        e0_idn = {pfg.base_to_int_idn(i) for i in e0_literal}
        pfg.add_element(e0_idn) 

        e1_literal = {5,6,12,31}
        e1_idn = {pfg.base_to_int_idn(i) for i in e1_literal}
        pfg.add_element(e1_idn)  

        # case: {5,6,12,31}
        q = pfg.i2f_map[9] 

        x = q[0](9,e1_idn) 
        assert x == [3, 4, 2, 1, 2, (3, 4), (3, 2), (4, 3), (2, 3)]

        # check for consistency 
        for _ in range(100): 
            assert q[0](9,e1_idn) == x 

        # case: identity 
        i4 = 4
        e4 = pfg.int_label_to_element(i4) 
        q2 = pfg.i2f_map[i4]
        x2 = q2[0](i4,e4) 
        assert x2 == [4] 

        # case: {5,6}

        i3 = pfg.element_to_int_label(e0_idn) 
        q3 = pfg.i2f_map[i3]
        x3 = q3[0](i3,e0_idn)  

        assert x3 == [2, 1, 1, 1, 1, 2, 1, 1, 2, 1, \
            (2, 1), (2, 1), (2, 2), (2, 1), (1, 2), \
            (1, 1), (1, 1), (1, 2), (1, 1), (1, 1), \
            (1, 1), (1, 1), (1, 2), (1, 1), (2, 2), \
            (2, 1), (1, 1), (1, 2)]

        # check for consistency 
        for _ in range(100): 
            assert q3[0](i3,e0_idn) == x3 

    def test__PRDCCFunctionGen__function_consistency__case_2(self): 

        pfg = sample_PRDCCFunctionGen_R311("P")  

        e0_literal = {5,6,67,112} 
        e0_idn = {pfg.base_to_int_idn(i) for i in e0_literal}
        pfg.add_element(e0_idn)

        q = pfg.i2f_map[8] 

        x = q[0](8,e0_idn)
        assert x == [5, 2, 6, 1, 1, 6]
        for _ in range(100): 
            assert q[0](8,e0_idn) == x 
        
        e1_literal = {67,112}
        e1_idn = {pfg.base_to_int_idn(i) for i in e1_literal}
        pfg.add_element(e1_idn) 

        x2 = q[0](8,e1_idn)
        assert x2 == [5, 6, 6, 5, 5, 6]
        for _ in range(100): 
            assert q[0](8,e1_idn) == x2 

    def test__PRDCCFunctionGen__hierarchy_of_elements__case_1(self):
        pfg = sample_PRDCCFunctionGen_R311("P")  

        e0_literal = {5,6,67,112} 
        e0_idn = {pfg.base_to_int_idn(i) for i in e0_literal}
        pfg.add_element(e0_idn)
        
        e1_literal = {67,112}
        e1_idn = {pfg.base_to_int_idn(i) for i in e1_literal}
        pfg.add_element(e1_idn) 


        e2 = {0,1,9} 
        pfg.add_element(e2)

        e3 = {2,5,10,8} 
        pfg.add_element(e3)

        e4 = {11,5} 
        pfg.add_element(e4)

        assert sorted(pfg.i2f_map.keys()) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


if __name__ == '__main__':
    unittest.main()