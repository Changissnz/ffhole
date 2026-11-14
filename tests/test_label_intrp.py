from falses.label_intrp import * 
import unittest


"""
py -m tests.test_label_intrp  
"""
class LabelInterpreterTypeCEEMethods(unittest.TestCase):

    def test__LabelInterpreterTypeCEE__label_to_s_methods__case_1(self): 
        label_seq = [5,4,3,17,56] 
        L = LabelInterpreterTypeCEE(label_seq) 

        skew = [(0,3),(3,2)] 
        d = 1 

        P = L.label_to_s_nodeset(4,deepcopy(skew),d,full_output=True)

        assert P == [(20, 56), (6, 4), (7, 4), (18, 17), (9, 4)]

        P2 = L.label_to_s_path(4,skew,d)

        q = [p[0] for p in P]
        for q_ in q: assert q_ in P2 
        assert P2 == [5, 10, 15, 20, 21, 16, 11, 6, 7, 8, 13, 18, 19, 14, 9]

    def test__LabelInterpreterTypeCEE__label_to_s_methods__case_2(self):
        label_seq = [5,4,3,17,56] 
        L = LabelInterpreterTypeCEE(label_seq)

        skew = [(0,1),(1,1),(2,2),(3,1),(4,1)] 
        d = 1 
        P = L.label_to_s_nodeset(5,deepcopy(skew),d,full_output=True)

        assert P == [(5, 4), (6, 4), (12, 3), (8, 4), (9, 4)]

        P0 = L.label_to_s_nodeset(5,deepcopy(skew),d,full_output=False) 
        assert P0 == [p[0] for p in P] 

        P2 = L.label_to_s_nodeset(5,[],d,full_output=False)
        assert P2 == L.l2p_map[5].p 

        d2 = -1 
        P3 = L.label_to_s_nodeset(5,deepcopy(skew),d2,full_output=True)
        assert P3 == [(20, 56), (21, 56), (17, 17), (23, 56), (24, 56)]

    def test__LabelInterpreterTypeCEE__path_to_lmap__case_1(self):
        label_seq = [5,4,3,17,56] 
        L = LabelInterpreterTypeCEE(label_seq)

        skew = [(0,4),(1,3),(4,1)]  
        d = 1 
        P = L.label_to_s_nodeset(4,deepcopy(skew),d,full_output=True)
        P2 = L.label_to_s_path(4,skew,d)

        assert P2 == [5, 0, 1, 6, 11, 16, 21, 22, 17, 12, 7, 8, 9, 14]

        M = L.path_to_lmap(P2)

        assert M == defaultdict(set, {0: {4, 5}, 1: {17, 3, 4, 5, 56}, \
            2: {56, 17, 3, 4}, 3: {4}, 4: {3, 4}})


if __name__ == '__main__':
    unittest.main()