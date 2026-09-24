from falses.false_entry_functions import * 
from morebs2.numerical_generator import prg__LCG

import unittest

def sample_FE_graph(): 
    return defaultdict(set,{0:{1,2},\
    1: {0,6},2:{0,3},3:{2,4,5},\
    4:{3,9},5:{3},6:{1,7},7:{6,10,12},\
    8:{6,11,12},9:{4,10},10:{7,9},\
    11:{8},12:{7,8}})

"""
py -m tests.test_false_entry_functions
"""
# NOTE: runtime on developer's device: approx. 180 seconds. 
class FalseEntryFunctions(unittest.TestCase):

    def test__possible_graph_traps__case_1(self): 
        G = defaultdict(set,{0: {1,2},\
            1:{0,2},\
            2: {0,1}}) 

        agent_locations = {"a":0,"b":2} 

        X = list(possible_graph_traps(G,agent_locations))
        assert X == [['a'],['b']]
        return 

    def test__possible_graph_traps__case_2(self):
        G2 = defaultdict(set,
            {0:{1,5,6,7},1:{0,2,3,4},2:{1},\
            3:{1},4:{1},5:{0,7},6:{0},\
            7:{0,5}})

        agent_locations2 = {"a":0,"b":1,"c":7} 
        X2 = list(possible_graph_traps(G2,agent_locations2))
        assert X2 == [['a'], ['b'], ['c']]

    def test__possible_graph_traps__case_3(self):
        G = sample_FE_graph() 
        agent_locations = {"a":0,"b":4,"c":3,"d":7} 
        XX = list(possible_graph_traps(G,agent_locations))

        assert XX == [['a', 'b', 'd'], ['c', 'd']]
        return

    def test__even_till_zero_distribution__case_1(self): 
        node_weight_map = {0:10,1:25,2:50,3:200,4:500}  
        node_weight_map2 = deepcopy(node_weight_map)
        central_node = 0 
        peripheral = {1,2,3}
        delta = 150 

        X = even_till_zero_distribution(node_weight_map,central_node,peripheral,delta)

        assert X[0] == {0: 160.0, 1: 0, 2: 0, 3: 125.0, 4: 500} 
        assert X[1] == True

        delta2 = -150 
        X2 = even_till_zero_distribution(node_weight_map,central_node,peripheral,delta2)
        assert X2[0] == {0: 10.0, 1: 50.0, 2: 50.0, 3: 175.0, 4: 500}
        assert X2[1] == True

        X3 = even_till_zero_distribution(deepcopy(node_weight_map2),central_node,peripheral,delta2)
        assert X3[0] == {0: -140, 1: 75.0, 2: 100.0, 3: 250.0, 4: 500}
        assert X3[1] == False

        delta3 = 276
        X4 = even_till_zero_distribution(deepcopy(node_weight_map2),central_node,peripheral,delta3)

        assert X4[0] == {0: 285, 1: 0, 2: 0, 3: 0, 4: 500}
        assert X4[1] == False

    def test__max_traps_with_boolean_conditional__case_1(self):
        G = sample_FE_graph() 

        agent_locations = {"a":0,"b":4,"c":3,"d":7} 
        node_to_expected_weight_range_map = {}
        node_weight_map = {0:20,1:25,2:30,3:15,4:40,5:12,6:32,\
            7:45,8:37,9:55,10:60,11:43,12:43} 

        node_to_expected_weight_range_map = {0: [30,40],3: [35,55],4: [10,20],7:[80,88]} 

        prg = prg__LCG(56,-13.33,-212,455.7)
        T = max_traps_with_boolean_conditional(G,agent_locations,node_to_expected_weight_range_map,\
            deepcopy(node_weight_map),prg)

        assert len(T[0]) == 1 

        T0_ans = {0: 30.0, 1: 20.0, 2: 25.0, 3: 25.0, 4: 20, 5: 12, \
            6: 20.33333, 7: 80.0, 8: 37, 9: 65.0, 10: 48.33333, 11: 43, 12: 31.33333} 
        assert {k:round(v,5) for k,v in T[0][0].items()} == T0_ans 

        ST0 = fetch_satisfied_traps(T[0][0],node_to_expected_weight_range_map)
        assert ST0 == {0, 4, 7} 

        # subcase 2 

        node_to_expected_weight_range_map[3] = [25,55]

        prg = prg__LCG(56,-13.33,-212,455.7)
        T2 = max_traps_with_boolean_conditional(G,agent_locations,node_to_expected_weight_range_map,\
            deepcopy(node_weight_map),prg)

        ST1 = fetch_satisfied_traps(T2[0][0],node_to_expected_weight_range_map)
        
        assert ST1 == {0,3,4,7} 

    def test__max_traps_with_boolean_conditional__case_2(self):

        G = defaultdict(set,{0:{1},\
            1: {0,2},2: {1,3}}) 

        agent_locations = {"a":0,"b":1,"c":3} 

        node_weight_map = {0:20,1:25,2:30,3:15}

        node_to_expected_weight_range_map = {0: [30,40],1: [25,55],3: [10,20]} 

        prg = prg__LCG(56,-13.33,-212,455.7)
        T = max_traps_with_boolean_conditional(G,agent_locations,node_to_expected_weight_range_map,node_weight_map,prg)
        assert len(T[0]) == 2 

        st_ans = [{0,3},{1,3}]
        for i,t in enumerate(T[0]): 
            st = fetch_satisfied_traps(t,node_to_expected_weight_range_map)
            assert st == st_ans[i] 

if __name__ == '__main__':
    unittest.main()