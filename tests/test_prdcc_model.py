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

        e0 = {5,6}
        pfg.add_element(e0) 

        assert set(pfg.l2f_map.keys()) == {i for i in range(8 + 1)} 

        assert pfg.element_to_int_label(e0) == 8 

        e1 = {5,6,12,31}
        pfg.add_element(e1)  
        assert pfg.element_to_int_label(e1) == 9 

        # try adding a phony element, 
        e2 = {5,6,112,235423}
        try: 
            pfg.add_element(e2) 
            assert False 
        except: 
            assert True 

        return 

    def test__PRDCCFunctionGen__function_consistency__case_1(self): 

        pfg = sample_PRDCCFunctionGen_R311("G")  

        e0 = {5,6}
        pfg.add_element(e0) 

        e1 = {5,6,12,31}
        pfg.add_element(e1)  

        # case: {5,6,12,31}
        q = pfg.l2f_map[9] 

        x = q[0](9,e1)
        assert x == [12, 31, 6, 5, 6, (12, 31), (12, 6), (31, 12), (6, 12)]

        for _ in range(100): 
            assert q[0](9,e1) == x 

        # case: identity 
        i4 = 4
        e4 = pfg.int_label_to_element(i4) 
        q2 = pfg.l2f_map[i4]
        x2 = q2[0](i4,e4) 
        assert x2 == [4] 

        # case: {5,6}

        i3 = pfg.element_to_int_label(e0) 
        q3 = pfg.l2f_map[i3]
        x3 = q3[0](i3,e0)  

        assert x3 == [6, 5, 5, 5, 5, 6, 5, 5, 6, 5, \
            (6, 5), (6, 5), (6, 6), (6, 5), (5, 6), (5, 5), \
            (5, 5), (5, 6), (5, 5), (5, 5), (5, 5), (5, 5), \
            (5, 6), (5, 5), (6, 6), (6, 5), (5, 5), (5, 6)]

        for _ in range(100): 
            assert q3[0](i3,e0) == x3 

    def test__PRDCCFunctionGen__function_consistency__case_2(self): 

        pfg = sample_PRDCCFunctionGen_R311("P")  

        e0 = {5,6,67,112} 
        pfg.add_element(e0) 

        q = pfg.l2f_map[8] 

        x = q[0](8,e0)
        assert x == [67, 6, 112, 5, 5, 112]
        for _ in range(100): 
            assert q[0](8,e0) == x 

        e1 = {67,112} 
        pfg.add_element(e1) 

        x2 = q[0](8,e1)
        assert x2 == [67, 112, 112, 67, 67, 112]
        for _ in range(100): 
            assert q[0](8,e1) == x2 

if __name__ == '__main__':
    unittest.main()