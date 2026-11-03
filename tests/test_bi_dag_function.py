from falses.bi_dag_function import * 
import unittest

###

"""
py -m tests.test_bi_dag_function 
""" 
class DAGTraversalFunctionTypeHSDMethods(unittest.TestCase):

    """
    demonstrates consistency of NEXT node function 
    """ 
    def test__DAGTraversalFunctionTypeHSD__next_from_node__case_1(self): 

        prg = prg__LCG(735.78,-1414.141,55.62,7143.61)

        S = SecretSpaceTypeDAG.generate_std_instance(prg)

        L = [int(prg()) for _ in range(14)] 
        N = NoiseAddedIterableContainer(L,int(prg())) 

        df = DAGTraversalFunctionTypeHSD(S.dag,N)
        hs_map = nodepath_to_s2l_map(S.dag,S.P)

        prg2 = prg__LCG(4435.78,414.141,-4455.62,7143.61)
        dag2 = SecretSpaceTypeDAG.generate_std_DAG(prg2)  

        # subcase 1: only 1 child 
        n = 113  
        result = 89 
        C = dag2.children_of_node(n)    
        assert 89 in C and len(C) == 1 
        for _ in range(20): 
            x = df.next_from_node(hs_map,dag2,n)
            assert x == result 

        # subcase 2: four children 
        n2 = 86  
        assert dag2.children_of_node(n2) ==  {120, 58, 45, 119}, "got {}".format(dag2.children_of_node(n2))
        x2 = df.next_from_node(hs_map,dag2,n2)
        result2 = 58
        assert result2 in dag2.children_of_node(n2)  

        for _ in range(20): 
            x2 = df.next_from_node(hs_map,dag2,n2)
            print("{} -> {}".format(n2,x2))
            assert x2 == result2, "got {}".format(x2) 
        return 

    """
    demonstrates variance of NEXT node over different DAG inputs. 
    """
    def test__DAGTraversalFunctionTypeHSD__next_from_node__case_2(self): 

        prg = prg__LCG(735.78,-1414.141,55.62,7143.61)

        L = [int(prg()) for _ in range(14)] 
        N = NoiseAddedIterableContainer(L,int(prg())) 

        prg2 = prg__LCG(4435.78,414.141,-4455.62,7143.61)
        dag2 = SecretSpaceTypeDAG.generate_std_DAG(prg2)  

        prg2 = prg__LCG(4435.78,414.141,-4455.62,7143.61)
        n = 25 
        X = defaultdict(int) 

        for _ in range(100): 
            S = SecretSpaceTypeDAG.generate_std_instance(prg)

            df = DAGTraversalFunctionTypeHSD(S.dag,N)
            hs_map = nodepath_to_s2l_map(S.dag,S.P)
            x2 = df.next_from_node(hs_map,dag2,n)
            X[x2] += 1 

        assert X == defaultdict(int, {122: 23, 4: 19, 7: 29, 52: 29})

if __name__ == '__main__':
    unittest.main()