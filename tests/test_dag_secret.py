from falses.dag_secret import * 
from morebs2.numerical_generator import prg__LCG
from morebs2.matrix_methods import vector_to_string
import unittest

###

"""
py -m tests.test_dag_secret 
""" 
class SecretSpaceTypeDAGMethods(unittest.TestCase):

    """
    tests uniqueness of calculated paths to node 10 in sample 
    <SecretSpaceTypeDAG>. 

    tests path differences between two different <SecretSpaceTypeDAG>s. 
    """
    def test__SecretSpaceTypeDAG__n_paths_with_node__case_1(self): 

        prg = prg__LCG(735.78,-1414.141,55.62,7143.61)

        # subcase 1 
        S = SecretSpaceTypeDAG.generate_std_instance(prg) 

        V = set() 
        for _ in range(20): 
            p = S.n_paths_with_node(10,1,prg)[0]
            ps = vector_to_string(p.p)
            V |= {ps} 
        assert len(V) == 20 

        # subcase 2 
        S2 = SecretSpaceTypeDAG.generate_std_instance(prg) 

        V2 = set() 
        for _ in range(20): 
            p = S2.n_paths_with_node(10,1,prg)[0]
            ps = vector_to_string(p.p)
            V2 |= {ps} 
        assert len(V2) == 20, "got {}".format(len(V2))

        d = (V - V2) | (V2 - V)
        assert len(d) == 40, "got {}".format(len(d)) 


    """
    demonstrates correct number of state-to-labelset pairs for generated map 
    """
    def test__generate_s2l_hyp_map__case_1(self): 

        prg = prg__LCG(3435.78,-4514.141,152.62,9843.61)

        dag = SecretSpaceTypeDAG.generate_std_DAG(prg,output_is_generator=False,\
            num_nodes_per_layer_range=[1,5])

        sec = dag.n_paths_with_node(20,1,False,prg)[0] 

        actual_s2l_map = nodepath_to_s2l_map(dag,sec)

        # subcase 1 
        correct_ratio = 0.5 
        M = generate_s2l_hyp_map(dag,actual_s2l_map,correct_ratio,prg)

        c = 0 
        for k,v in M.items(): 
            if v == actual_s2l_map[k]: 
                c += 1 
        assert c == 5 

        # subcase 2
        correct_ratio = 0.2 
        M_ = generate_s2l_hyp_map(dag,actual_s2l_map,correct_ratio,prg)

        c = 0 
        for k,v in M_.items(): 
            if v == actual_s2l_map[k]: 
                c += 1 
        assert c == 2, "got {}".format(c) 

    """
    demonstrates expected number of state-to-labelset pairs for generated map 
    cannot be achieved, due to too many single-node layers. 
    """
    def test__generate_s2l_hyp_map__case_2(self): 

        prg2 = prg__LCG(35.78,-14514.141,752.62,6843.61)

        dag2 = SecretSpaceTypeDAG.generate_std_DAG(prg2,output_is_generator=False,\
            num_nodes_per_layer_range=[1,1])

        sec2 = dag2.n_paths_with_node(5,1,False,prg2)[0] 

        actual_s2l_map2 = nodepath_to_s2l_map(dag2,sec2)
        correct_ratio = 0.5 

        M2 = generate_s2l_hyp_map(dag2,actual_s2l_map2,correct_ratio,prg2)

        c2 = 0 
        for k,v in M2.items(): 
            if v == actual_s2l_map2[k]: 
                c2 += 1 
        assert c2 == 15 == len(dag2.l2n_map) 

if __name__ == '__main__':
    unittest.main()