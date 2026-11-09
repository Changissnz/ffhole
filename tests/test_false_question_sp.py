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
        assert len(F.Q.act_hyp) == 7 

        tails = set() 
        for x in F.Q.act_hyp.gpaths: 
            tails |= {x.tail()} 

        assert len(tails) == len(next_nodes) 
        assert next_nodes.intersection(tails) == {1016, 881, 15, 289}

        # check for correct non-null feedback
        ans = {1016: (False, False), 815: (False, False), \
            289: (None, None), 881: (False, True), \
            246: (None, None), 15: (None, None), \
            1112: (None, None)}
        assert F.Q.tail2fb_map == ans 
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
            1: {881, 289, 815, 246, 1112, 1016, 15}})

        assert F.Q.act_hyp.path_hyp == ans 

        X = F.Q.current_action_sequence_hyp()
        for k,v in X.items(): 
            assert v.issubset(ans[k]) 
        assert X[0] != ans[0]
        assert X[1] == ans[1]

        assert F.obj_2_score() == (2, 2, 49)

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
        assert s2 == ({2, 4, 6, 7}, 10)

    """
    shows performance of a questioner against a subject in False Question Type SP. 

            The End Results: 
    Questioner knows 114 out of the 139 actions taken by subject. Questioner 
    knows all categories for subject's hidden state. 
    """
    def test__FalseQuestionTypeSP__next__case_2(self): 
        print("\t\t** False Question Type SP: Case #2")
        initial_q_hypothesis_correct_ratio = 0.2 
        prg = prg__LCG(3435.78,-4514.141,152.62,9843.61)

        F = FalseQuestionTypeSP.generate_std_instance(initial_q_hypothesis_correct_ratio,prg)

        while not F.fin_stat:  
            next(F) 
            '''
            F.Q.act_hyp.display_paths(1) 
            print()
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n" * 2) 
            '''

        assert F.obj_1_score() == ({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, 10)
        assert F.obj_2_score() == (114, 139, 1)

    """
    Questioner uncovers 6/21 categories of subject's hidden state. 
    Questioner knows 21/126 actions taken by subject. 
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
        assert len(score_01[0]) == 6 
        assert score_01[1] == 21
        assert score_01[2] == 126
        assert F.obj_2_score() == (26, 145, 1)

    """
    False Question Type SP case is the same as Case #2, except Questioner operates with 
    another PRNG. Results demonstrate performance differences. 

            The End Results: 
    Questioner knows 15/139 actions taken by subject. Questioner knows 5/10 categories 
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

        assert score_01 == ({5, 6, 7, 8, 9}, 10, 131)
        assert score_11 == (15, 139, 1) 


if __name__ == '__main__':
    unittest.main()