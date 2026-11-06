from falses.bi_dag_function import * 
import unittest

def sample_ActionGraphANDSecretSpace__FIRST(): 
    prg = prg__LCG(735.78,-1414.141,55.62,7143.61)

    S = SecretSpaceTypeDAG.generate_std_instance(prg) 
    s2l_map = S.secret_path_map() 

    A = ActionGraphTypeDAGLT.generate_std_instance(prg,s2l_map)

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
        assert c == 2  

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

    """
    demonstrates < 1% rate of Trues for 600-700 state-to-label maps. 
    """
    def test__ActionGraphTypeDAGLT__boolean_output__case_3(self): 

        A,S,prg = sample_ActionGraphANDSecretSpace__FIRST() 

        V = prg_seqsort(sorted(S.dag.G.keys()),prg) 
        D = defaultdict(int)

        for v in V: 
            p = S.n_paths_with_node(v,10)
            for p_ in p: 

                pmap = nodepath_to_s2l_map(S.dag,p_) 
                D[A.boolean_output(45,pmap)] += 1 

        assert D == defaultdict(int,{False: 664, True: 6}) 

if __name__ == '__main__':
    unittest.main()