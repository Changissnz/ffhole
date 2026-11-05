from falses.bi_dag_function import * 
import unittest

def sample_ActionGraphANDSecretSpace__FIRST(): 
    prg = prg__LCG(735.78,-1414.141,55.62,7143.61)

    S = SecretSpaceTypeDAG.generate_std_instance(prg) 
    s2l_map = S.secret_path_map() 

    A = ActionGraphTypeDAGLT.generate_std_ActionGraphTypeDAGLT(prg,s2l_map)

    return A,S,prg 
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

class ActionGraphTypeDAGLTMethods(unittest.TestCase):

    """ 
    demonstrates consistency of `wfunc`,`vfunc`, and `tfunc` output on 
    one node of an Action Graph
    """
    def test__ActionGraphTypeDAGLT__function_variables__case_1(self): 

        A,_,_ = sample_ActionGraphANDSecretSpace__FIRST() 

        node = 45 
        q = A.wfunc(node)
        q1 = A.vfunc(node) 
        q2 = A.tfunc(node) 

        w45 = np.array([74.60531, 82.4628 , 74.21899, 98.80109])
        v45 = [9, 2, 6, 4]
        T = set([q2])

        assert np.all(w45 == q) 
        assert np.all(v45 == q1)
        assert 0 <= q2 <= 1. 

        for _ in range(100): 
            assert np.all(A.wfunc(node) == q)
            assert np.all(A.vfunc(node) == q1)
            T |= {A.tfunc(node)}
        assert len(T) == 1 

    """
    demonstrates correct activation threshold booleans for two 
    cases of state-to-label map inputs. 
    """
    def test__ActionGraphTypeDAGLT__boolean_output__case_1(self):

        A,_,_ = sample_ActionGraphANDSecretSpace__FIRST() 

        v45 = A.vfunc(45) 
        w45 = A.wfunc(45) 

        M = {k:False for k in A.G.keys()}

        # subcase 1 
        M0 = deepcopy(M) 
        M0[v45[0]],M0[v45[2]] = deepcopy(A.s2l_map[v45[0]]),deepcopy(A.s2l_map[v45[2]]) 
        assert not A.boolean_output(45,M0)
        assert (w45[0] + w45[2]) / np.sum(w45) < A.tfunc(45) == 0.5 

        # subcase 2 
        M1 = deepcopy(M) 
        M1[v45[2]],M1[v45[3]] = deepcopy(A.s2l_map[v45[2]]),deepcopy(A.s2l_map[v45[3]]) 
        assert A.boolean_output(45,M1)
        assert (w45[2] + w45[3]) / np.sum(w45) >= A.tfunc(45) == 0.5 

    """
    demonstrates straight Falses from activation function over n arbitrary 
    paths from secret. 
    """
    def test__ActionGraphTypeDAGLT__boolean_output__case_2(self): 

        A,S,prg = sample_ActionGraphANDSecretSpace__FIRST() 

        V = prg_seqsort(sorted(S.dag.G.keys()),prg) 
        D = defaultdict(int)

        for v in V: 
            p = S.n_paths_with_node(v,3)
            for p_ in p: 
                pmap = nodepath_to_s2l_map(S.dag,p_) 
                print("PMAP")
                print(pmap)
                D[A.boolean_output(45,pmap)] += 1 

        assert D == defaultdict(int,{False:201}) 
        assert sum(D.values()) == len(V) * 3 

if __name__ == '__main__':
    unittest.main()