from falses.hyp_container_gp import * 
import unittest

"""
py -m tests.test_hyp_container_gp
"""
class HypothesisContainerTypeGPMethods(unittest.TestCase):

    def test__HypothesisContainerTypeGP__multiple_methods__case_1(self): 
        H = HypothesisContainerTypeGP(num_paths_per_tail_node=2) 
        H.load_starting_nodes({0,1,2,3,4}) 
        assert len(H) == 5 
        assert len(H.tail2paths) == 5 

        P = H[2]
        P2 = H[3]

        P_ = H.update_path(deepcopy(P),next_node=14,next_weight=1) 
        P2_ = H.update_path(deepcopy(P2),next_node=14,next_weight=0) 

        H.delete_path(P) 
        assert len(H) == 4 
        assert set(H.tail2paths.keys()) == {0, 1, 3, 4}

        H.delete_path(P2) 
        assert len(H) == 3 
        assert set(H.tail2paths.keys()) == {0, 1, 4}

        # add two updated paths from P back into memory 
        H.add_path_to_mem(P_) 
        H.add_path_to_mem(P2_) 
        assert len(H) == 3  
        assert set(H.tail2paths.keys()) == {0, 1, 4,14}

        # flush the queue 
        H.flush_queue() 

        heads = [] 
        for x in H.tail2paths[14]: 
            heads.append(x.head())
        assert heads == [2,3] 
        assert len(H) == 5 

        # add another path with tail at 14 
        P4 = NodePath(321)
        P4.append(14,10) 
        H.add_path_to_mem(P4) 
        H.flush_queue() 

        # check for correct sizes 
        for x in H.gpaths: 
            print(x.p)

        assert len(H) == 5, "got {}".format(len(H))

        heads.clear() 
        for x in H.tail2paths[14]: 
            heads.append(x.head())
        assert heads == [321,2] 

if __name__ == '__main__':
    unittest.main()