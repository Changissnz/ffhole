from falses.hyp_container_gp import * 
from morebs2.numerical_generator import prg__LCG 
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
        H.flush_queue(False) 

        heads = [] 
        for x in H.tail2paths[14]: 
            heads.append(x.head())
        assert heads == [2,3] 
        assert len(H) == 5 

        # add another path with tail at 14 
        P4 = NodePath(321)
        P4.append(14,10) 
        H.add_path_to_mem(P4) 
        H.flush_queue(False) 

        # check for correct sizes 
        for x in H.gpaths: 
            print(x.p)

        assert len(H) == 5, "got {}".format(len(H))

        heads.clear() 
        for x in H.tail2paths[14]: 
            heads.append(x.head())
        assert heads == [321,2] 

    def test__HypothesisContainerTypeGP__multiple_methods__case_2(self):
        H = HypothesisContainerTypeGP(num_paths_per_tail_node=3) 
        H.load_starting_nodes({0,1,2,3,4}) 

        prg = prg__LCG(-3452.234,654.3,-432.77,90021.62) 

        # update every path to next node = 14. 
        for p in H.gpaths: 
            p2 = H.update_path(deepcopy(p),next_node=14,next_weight=int(prg() % 2)) 
            H.add_path_to_mem(p2)

        # check for max of 3 tails for tail=14. 
        H.flush_queue(True)   
        assert len(H) == 3 

        p2 = H.update_path(deepcopy(H.gpaths[0]),next_node=25,next_weight=1) 
        H.add_path_to_mem(p2,prg=prg)

        p3 = H.update_path(deepcopy(H.gpaths[1]),next_node=25,next_weight=0) 
        H.add_path_to_mem(p3,prg=prg)

        p4 = H.update_path(deepcopy(H.gpaths[2]),next_node=25,next_weight=1) 
        H.add_path_to_mem(p4,prg=prg)

        # check for correct order after sorting
        H.flush_queue(True)   
        L = H.tail2paths[25]
        for i in range(1,len(L)):
            assert L[i].cost() <= L[i-1].cost()

        assert len(H) == 3 


if __name__ == '__main__':
    unittest.main()