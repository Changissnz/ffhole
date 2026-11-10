from automatons.false_question_sp import * 
from morebs2.numerical_generator import prg_to_prg__LCG_sequence__v2,merge_two_prgs
from morebs2.measures import zero_div_
import unittest

###

"""
py -m tests.test_false_question_sp
""" 
class FalseQuestionTypeSPMethods(unittest.TestCase):

    """
    ensures correct starting variables: Q's hypotheses. 
    """ 
    def test__FalseQuestionTypeSP__init__case_1(self): 
        initial_q_hypothesis_correct_ratio = 0.2 
        prg = prg__LCG(3435.78,-4514.141,152.62,9843.61)
        F = FalseQuestionTypeSP.generate_std_instance(initial_q_hypothesis_correct_ratio,prg)

        assert len(F.action_graph.leaf_nodeset()) == 10 
        assert len(F.action_graph.l2n_map[0]) == 11 

        # one hypothesis per root node 
        heads = set() 
        for x in F.Q.act_hyp.gpaths: 
            heads |= {x.head()} 
        assert F.action_graph.l2n_map[0] == heads
        return 

    """
    ensures that after automaton moves one timestamp, 
    Q does not have any two hypotheses with the same tail node. 

    Also demonstrates that the `next_from_node` method of 
    <DAGTraversalFunctionTypeHSD> changes through the course of 
    improving every hypothesis, due to Q's changing hypothesis 
    on S' hidden state. 
    """ 
    def test__FalseQuestionTypeSP__next__case_1(self): 
        initial_q_hypothesis_correct_ratio = 0.2 
        prg = prg__LCG(3435.78,-4514.141,152.62,9843.61)
        F = FalseQuestionTypeSP.generate_std_instance(initial_q_hypothesis_correct_ratio,prg)

        assert len(F.action_graph.leaf_nodeset()) == 10 
        assert len(F.action_graph.l2n_map[0]) == 11 

        # one hypothesis per root node 
        heads = set() 
        for x in F.Q.act_hyp.gpaths: 
            heads |= {x.head()} 
        assert F.action_graph.l2n_map[0] == heads

        #

        T = F.action_graph_op
        H = F.Q.current_hidden_state_hyp()

        next_nodes = set() 
        for n in F.action_graph.l2n_map[0]: 
            n2 = T.next_from_node(H,F.action_graph,n)
            next_nodes |= {n2} 

        next(F) 

        # Q has to iterate through every hypothesis
        assert F.Q.hyp_index == 11 

        # number of hypothesis has been reduced because of duplicate tails 
        assert len(F.Q.act_hyp) == 8 

        tails = set() 
        for x in F.Q.act_hyp.gpaths: 
            tails |= {x.tail()} 
        assert tails == {881, 753, 275, 246, 1112, 1016, 173, 15}

        assert next_nodes == {881, 753, 289, 1016, 173, 15}
        assert next_nodes.intersection(tails) == {173, 15, 881, 753, 1016}

        # check for correct non-null feedback
            # duplicate @ node 246
        ans = {1016: (None, None), 173: (None, None), 15: (None, None), \
            1112: (None, None), 881: (None, None), 753: (None, None), \
            246: (None, None), 275: (None, None)}

        assert F.Q.tail2fb_map == ans, "got {}".format(F.Q.tail2fb_map)
        assert set(F.Q.tail2fb_map.keys()) == tails


    """
    demonstrates correctness of questioner's hypothesis on action sequence, via 
    method<obj_score_2>. 
    """
    def test__FalseQuestionTypeSP__Questioner_current_action_sequence_hyp__case_1(self):

        initial_q_hypothesis_correct_ratio = 0.2 
        prg = prg__LCG(3435.78,-4514.141,152.62,9843.61)

        F = FalseQuestionTypeSP.generate_std_instance(initial_q_hypothesis_correct_ratio,prg)

        T = F.action_graph_op
        H = F.Q.current_hidden_state_hyp() 

        next_nodes = set() 
        for n in F.action_graph.l2n_map[0]: 
            n2 = T.next_from_node(H,F.action_graph,n)
            next_nodes |= {n2} 

        next(F) 

        ans = defaultdict(set, {0: {128, 929, 640, 1185, 934, \
            935, 1254, 526, 979, 698, 1021}, \
            1: {881, 753, 275, 246, 1112, 1016, 173, 15}})

        assert F.Q.act_hyp.path_hyp == ans, "got {}".format(F.Q.act_hyp.path_hyp)

        X = F.Q.current_action_sequence_hyp()
        for k,v in X.items(): 
            assert v.issubset(ans[k]) 
        assert X[0] != ans[0]
        assert X[1] == ans[1]

        assert F.obj_2_score() == (2, 2, 64)


    """
    demonstrates Q's hypothesis on the hidden state of S, before and after one timestamp. 
    """
    def test__FalseQuestionTypeSP__obj_1_score__case_1(self): 
        initial_q_hypothesis_correct_ratio = 0.2 
        prg = prg__LCG(3435.78,-4514.141,152.62,9843.61)

        F = FalseQuestionTypeSP.generate_std_instance(initial_q_hypothesis_correct_ratio,prg)

        s1 = F.obj_1_score()
        assert s1[0] == {2,5} 
        assert s1[1] == 10 

        next(F) 

        s2 = F.obj_1_score()
        assert s2 == ({2}, 10), "got {}".format(s2) 

    """
    shows performance of a questioner against a subject in False Question Type SP. 

            The End Results: 
    Questioner knows 18/139 actions taken by subject. Questioner 
    knows 9/10 categories for subject's hidden state, no improvement before and 
    after false questioning. 
    """
    def test__FalseQuestionTypeSP__next__case_2(self): 
        print("\t\t** False Question Type SP: Case #2")
        initial_q_hypothesis_correct_ratio = 0.2 
        prg = prg__LCG(3435.78,-4514.141,152.62,9843.61)

        F = FalseQuestionTypeSP.generate_std_instance(initial_q_hypothesis_correct_ratio,prg)
        Q = F.obj_1_score()
        assert F.obj_1_score() == ({2,5}, 10)

        while not F.fin_stat:  
            next(F) 
            '''
            F.Q.act_hyp.display_paths(1) 
            print()
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n" * 2) 
            '''

        assert F.obj_1_score() == ({1, 2, 3, 4, 5, 6, 7, 8, 9}, 10), "got {}".format(F.obj_1_score())
        assert F.obj_2_score() == (18, 139, 1), "got {}".format(F.obj_2_score())

    """
    Questioner uncovers 8/21 categories of subject's hidden state. 
    Questioner knows 32/145 actions taken by subject. 
    """
    def test__FalseQuestionTypeSP__next__case_3(self): 
        print("\t\t** False Question Type SP: Case #3")
        initial_q_hypothesis_correct_ratio = 0.2 
        prg0 = prg__LCG(3435.78,-4514.141,152.62,9843.61)
        prg1 = prg_to_LCG_stack(prg0,5,[add,sub])
        prg2 = prg_to_LCG_stack(prg1,3,[zero_div_,add]) 
        prg = merge_two_prgs(prg1,prg2,add) 

        F = FalseQuestionTypeSP.generate_std_instance(initial_q_hypothesis_correct_ratio,prg)

        score_0 = F.obj_1_score(True)
        assert len(score_0[0]) == 5 == ceil(score_0[1] * initial_q_hypothesis_correct_ratio) 
        assert score_0[1] == 21
        assert score_0[2] == 0 

        while not F.fin_stat:  
            F.Q.act_hyp.display_paths(1)
            print()
            next(F) 

        score_01 = F.obj_1_score(True) 
        assert len(score_01[0]) == 8, "got {}".format(score_01)
        assert score_01[1] == 21
        assert score_01[2] == 88

        score_11 = F.obj_2_score()
        assert score_11 == (32, 145, 1), "got {}".format(score_11)


    """
    False Question Type SP case is the same as Case #2, except Questioner operates with 
    another PRNG. Results demonstrate performance differences. 

            The End Results: 
    Questioner knows 20/139 actions taken by subject. Questioner knows 3/10 categories 
    for subject's hidden state. 
    """
    def test__FalseQuestionTypeSP__next__case_4(self): 
        print("\t\t** False Question Type SP: Case #4")

        initial_q_hypothesis_correct_ratio = 0.2 
        prg = prg__LCG(3435.78,-4514.141,152.62,9843.61)

        F = FalseQuestionTypeSP.generate_std_instance(initial_q_hypothesis_correct_ratio,prg)

        prg1 = prg_to_LCG_stack(prg,5,[add,sub])
        prg2 = prg_to_LCG_stack(prg1,3,[zero_div_,add]) 
        F.set_prg(prg2,False) 

        score_0 = F.obj_1_score(True)
        assert score_0 == ({2, 5}, 10, 0)

        while not F.fin_stat:  
            next(F) 
            #F.Q.act_hyp.display_paths(1) 

        score_01 = F.obj_1_score(True) 
        score_11 = F.obj_2_score() 

        assert score_01 == ({5,6,7}, 10, 1), "got {}".format(score_01)
        assert score_11 == (20, 139, 1), "got {}".format(score_11) 

    """
    False Question Type SP case is the same as Case #2, except Questioner operates with 
    another PRNG. Questioner is also given certain knowledge of subject's hidden state before 
    the automaton proceeds, which would likely result in a perfect score. 

            The End Results: 
    Questioner knows 137/139 actions taken by subject. Questioner knows 10/10 categories 
    for subject's hidden state. 
    """
    def test__FalseQuestionTypeSP__next__case_5(self): 
        print("\t\t** False Question Type SP: Case #5")

        initial_q_hypothesis_correct_ratio = 0.2 
        prg = prg__LCG(3435.78,-4514.141,152.62,9843.61)

        F = FalseQuestionTypeSP.generate_std_instance(initial_q_hypothesis_correct_ratio,prg)
        M = F.subject.de_secret.secret_path_map()
        for k,v in M.items(): 
            F.Q.hs_hyp_mach.set_certain_category(k,v)

        prg1 = prg_to_LCG_stack(prg,5,[add,sub])
        F.set_prg(prg1,False)  

        score_0 = F.obj_1_score(True)
        assert score_0 == ({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, 10, 0)

        while not F.fin_stat:  
            next(F) 
            #F.Q.act_hyp.display_paths(1) 

        score_01 = F.obj_1_score(True) 
        score_11 = F.obj_2_score(True) 

        assert score_01 == ({0, 1, 2, 3, 4,5, 6, 7, 8, 9}, 10, 1)

        assert score_11 == ([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, \
            12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,\
            24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, \
            36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, \
            48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, \
            60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, \
            72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, \
            84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, \
            96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, \
            107, 108, 109, 110, 111, 112, 113, 114, 115, 116, \
            117, 118, 119, 120, 121, 122, 123, 124, 125, 126, \
            127, 128, 129, 130, 131, 132, 133, 134, 135, 136, \
            137, 138], 139, 1)


    """
    False Question Type SP case is the same as Case #2, except Questioner operates with 
    another PRNG. Questioner is also given certain knowledge of subject's hidden state before 
    the automaton proceeds, which would likely result in a perfect score. 

            The End Results: 
    Questioner knows 139/139 actions taken by subject. Questioner knows 10/10 categories 
    for subject's hidden state. 
    """
    def test__FalseQuestionTypeSP__next__case_6(self): 
        print("\t\t** False Question Type SP: Case #6")

        initial_q_hypothesis_correct_ratio = 0.2 
        prg = prg__LCG(3435.78,-4514.141,152.62,9843.61)

        F = FalseQuestionTypeSP.generate_std_instance(initial_q_hypothesis_correct_ratio,prg,\
            act_function_type=2)
        M = F.subject.de_secret.secret_path_map()
        for k,v in M.items(): 
            F.Q.hs_hyp_mach.set_certain_category(k,v)

        prg1 = prg_to_LCG_stack(prg,5,[add,sub])
        F.set_prg(prg1,False)  

        score_0 = F.obj_1_score(True)
        assert score_0 == ({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, 10, 0)

        while not F.fin_stat:  
            next(F) 
            #F.Q.act_hyp.display_paths(1) 

        score_01 = F.obj_1_score(True) 
        score_11 = F.obj_2_score(False) 

        assert score_01 == ({0, 1, 2, 3, 4,5, 6, 7, 8, 9}, 10, 1)

        assert score_11 == (139, 139, 1)


if __name__ == '__main__':
    unittest.main()