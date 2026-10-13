from falses.graph_node_labeller import * 
from xFS_bots.graph_models.graph_gen import * 
import unittest

def sample_graph_V30(): 
    is_dsg = False 
    prg = prg__LCG(80.21,-512.5,521.54,6767.7) 
    is_realtime_gen = True 
    vertex_degree = 30 
    edge_connectivity = 0.2 
    verbose = False 

    gg = GraphGen(is_dsg,prg,is_realtime_gen,\
        vertex_degree,edge_connectivity,verbose)
    gg.full_run() 
    G = gg.d 

    G = graph_to_one_component(G,prg)
    return G,prg 

"""
py -m tests.test_graph_node_labeller
"""
# NOTE: runtime on developer's device: approx. 180 seconds. 
class NodeLabellingFunctionTypeSGAMethods(unittest.TestCase):

    def test__NodeLabellingFunctionTypeSGA__next__case_1(self): 
        G,prg = sample_graph_V30() 

        start_node = 2 
        is_bfs = True 
        label_set = {i for i in range(7)} 
        activation_function_type = "both"
        verbose = True 

        F = NodeLabellingFunctionTypeSGA(G,start_node,is_bfs,\
            label_set,activation_function_type,prg,verbose)

        nodeset_seq = [] 
        while not F.fin_stat: 
            q = next(F) 
            nodeset_seq.append(q) 

        assert nodeset_seq == [[9, 0, 11, 16, 17, 7, 26, 15, 3, 5],\
            [19, 10, 28, 21, 6, 20, 4, 1], [29], [14, 18],\
            [24], [22], [8], [13, 27], [25], [12], [23],\
            None]

        assert F.node2label_map == {2: 3, 9: 3, 0: 3, 11: 1, 16: 4,\
            17: 1, 7: 6, 26: 4, 15: 5, 3: 1, 5: 4, 19: 0, 10: 6,\
            28: 2, 21: 2, 6: 6, 20: 5, 4: 4, 1: 5, 29: 4, 14: 4,\
            18: 6, 24: 0, 22: 3, 8: 0, 13: 4, 27: 4, 25: 1, 12: 1,\
            23: 0}


if __name__ == '__main__':
    unittest.main()