from falses.chained_label_intrp import * 
import unittest

"""
py -m tests.test_chained_label_intrp 
""" 
class AGChainedLabelInterpreterTypeCEEMethods(unittest.TestCase):

    """
    checks for correct values in data structures after two S-path (skew path) 
    updates, producing a total of 3 links to the chain. 
    """ 
    def test__AGChainedLabelInterpreterTypeCEE__update_with_s_path__case_1(self): 

        c2w = {"sdfgsda":0.5,"46sdgf":0.55,"hs345as":0.2433,"jl;j":0.8812}

        prg = prg = prg__LCG(234.52,-352.2,11563.44,3449.65) 
        form_type = "G"

        AL = AGChainedLabelInterpreterTypeCEE(c2w,prg,form_type)

        starting_keys = {0, 1, 2, 3} 
        assert set(AL.I.l2p_map.keys()) == starting_keys
        assert set(AL.K.weight_map.keys()) == starting_keys
        assert set(AL.pfgen.i2f_map.keys()) == starting_keys

        skew = [(0,2),(1,3),(2,1)] 

        label = 0 
        AL.update_with_s_path(label,skew,skew_direction=1)
        assert AL.I.label_seq == [0, 1, 2, 3, 4, 5, 6, 7], "got {}".format(AL.I.label_seq)


        w0 = set(AL.I.l2p_map.keys())
        w0_ans = {0, 1, 2, 3, 4, 5, 6, 7} 
        assert w0 == w0_ans

        w1 = set(AL.K.weight_map.keys())
        w1_ans = {3, 0, 1, 2, (0, 2), (0, 0), (0, 1), (2, 0), (2, 2), \
            (1, 2), (1, 0), (2, 1), 4, (3, 2), (3, 3), (2, 3), \
            5, 6, 7}
        assert w1 == w1_ans 

        w2 = set(AL.pfgen.i2f_map.keys())
        assert w2 == w0_ans
        assert AL.pfgen.l2i_map.imap == {'0': 0, '1': 1, '2': 2, '3': 3, '0,1,2': 4, '2,3': 5, '1,2,3': 6, '0,1': 7}

        label2 = 7
        AL.update_with_s_path(label2,[],skew_direction=1)

        assert AL.I.label_seq == [0, 1, 2, 3, 4, 5, 6, 7], "got {}".format(AL.I.label_seq)
        assert len(AL) == 3
        # no change in label sets b/t Label Interpreters
        assert AL[1].label_seq == AL.I.label_seq

    """
    checks that labet set maintains size after new link is added; `maintain_constant_dim`
    set to True
    """
    def test__AGChainedLabelInterpreterTypeCEE__update_with_s_path__case_2(self): 
        c2w = {"sdfgsda":0.5,"46sdgf":0.55,"hs345as":0.2433,"jl;j":0.8812}

        prg = prg = prg__LCG(234.52,-352.2,11563.44,3449.65) 
        form_type = "G"

        AL = AGChainedLabelInterpreterTypeCEE(c2w,prg,form_type,maintain_constant_dim=True)

        starting_keys = {0, 1, 2, 3} 
        assert set(AL.I.l2p_map.keys()) == starting_keys
        assert set(AL.K.weight_map.keys()) == starting_keys
        assert set(AL.pfgen.i2f_map.keys()) == starting_keys

        skew = [(0,2),(1,3),(2,1)] 

        label = 0 #"46sdgf"
        AL.update_with_s_path(label,deepcopy(skew),skew_direction=1)

        assert len(AL.I) == len(AL.i_chain[0]) 
        assert AL.I.label_seq == [4, 5, 6, 7]

    """
    checks that the S-path instability vector calculated is a concatenation of 
    every index's instability vector. 
    """
    def test__AGChainedLabelInterpreterTypeCEE__s_path_instability_vec__case_1(self): 

        c2w = {"sdfgsda":0.5,"46sdgf":0.55,"hs345as":0.2433,"jl;j":0.8812}

        prg = prg = prg__LCG(234.52,-352.2,11563.44,3449.65) 
        form_type = "G"

        AL = AGChainedLabelInterpreterTypeCEE(c2w,prg,form_type)

        starting_keys = {0, 1, 2, 3} 
        assert set(AL.I.l2p_map.keys()) == starting_keys
        assert set(AL.K.weight_map.keys()) == starting_keys
        assert set(AL.pfgen.i2f_map.keys()) == starting_keys

        skew = [(0,2),(1,3),(2,1)] 

        label = 0
        AL.update_with_s_path(label,deepcopy(skew),skew_direction=1)

        label2 = 7
        AL.update_with_s_path(label2,[],skew_direction=1)

        # subcase 1: w/ non-zero skew 
        r = AL.s_path_instability_vec(0,label,skew,skew_direction=1,verbose=True)

        c0 = AL.constituents_to_label({0,1,2})
        c1 = AL.constituents_to_label({2,3})
        c2 = AL.constituents_to_label({1,2,3})
        c3 = AL.constituents_to_label({0,1})

        v0 = AL.element_instability_vec(c0) 
        v1 = AL.element_instability_vec(c1) 
        v2 = AL.element_instability_vec(c2) 
        v3 = AL.element_instability_vec(c3) 

        V = deepcopy(v0) 
        V.extend(v1) 
        V.extend(v2) 
        V.extend(v3) 

        assert r == V 

        # subcase 2: w/ zero skew 
        assert AL.element_instability_vec(label) == [0.55] * 2 

        r = AL.s_path_instability_vec(0,label,[],skew_direction=1,verbose=False) 
        assert r == [0.55] * len(AL.fetch_intrp(0)) * 2 

    def test__AGChainedLabelInterpreterTypeCEE__revert_to_chain_link__case_1(self):
        c2w = {"sdfgsda":0.5,"46sdgf":0.55,"hs345as":0.2433,"jl;j":0.8812}
        prg = prg = prg__LCG(234.52,-352.2,11563.44,3449.65) 
        form_type = "G"

        AL = AGChainedLabelInterpreterTypeCEE(c2w,prg,form_type,maintain_constant_dim=False)

        starting_keys = {0, 1, 2, 3} 
        assert set(AL.I.l2p_map.keys()) == starting_keys
        assert set(AL.K.weight_map.keys()) == starting_keys
        assert set(AL.pfgen.i2f_map.keys()) == starting_keys

        skew = [(0,2),(1,3),(2,1)] 

        label = 0 
        AL.update_with_s_path(label,deepcopy(skew),skew_direction=1)

        skew = [(0,2),(1,3),(2,1),(3,4),(5,3)]  
        AL.update_with_s_path(label,deepcopy(skew),skew_direction=1)

        skew = [(0,2),(2,7),(4,10),(7,3)]  
        AL.update_with_s_path(label,deepcopy(skew),skew_direction=1)

        i2 = deepcopy(AL.i_chain[2])

        # subcase 1
        AL.revert_to_chain_link(2)

        assert len(AL.i_chain) == 2 
        assert type(AL.I) == LabelInterpreterTypeCEE
        assert AL.I.label_seq == i2.label_seq

        # subcase 2
        AL.revert_to_chain_link(2) 
        assert AL.I.label_seq == i2.label_seq

    def test__AGChainedLabelInterpreterTypeCEE__reset_base__case_1(self):

        c2w = {"sdfgsda":0.5,"46sdgf":0.55,"hs345as":0.2433,"jl;j":0.8812}

        prg = prg = prg__LCG(234.52,-352.2,11563.44,3449.65) 
        form_type = "G"

        AL = AGChainedLabelInterpreterTypeCEE(c2w,prg,form_type,maintain_constant_dim=False)

        starting_keys = {0, 1, 2, 3} 
        assert set(AL.I.l2p_map.keys()) == starting_keys
        assert set(AL.K.weight_map.keys()) == starting_keys
        assert set(AL.pfgen.i2f_map.keys()) == starting_keys

        skew = [(0,2),(1,3),(2,1)] 

        label = 0 
        AL.update_with_s_path(label,deepcopy(skew),skew_direction=1)

        label2 = 7 
        skew2 = [(0,4),(2,5),(4,1),(5,6)] 
        AL.update_with_s_path(label2,deepcopy(skew2),skew_direction=1)

        label3 = 11 
        skew3 = [(0,4),(2,5),(4,1),(5,6),(7,2),(8,2),(9,5)]  
        AL.update_with_s_path(label3,deepcopy(skew3),skew_direction=1)

        label4 = 16 
        skew4 = [(0,2),(2,1),(4,5),(5,2),(7,6),(8,9),(12,5),(14,6),(16,17)] 
        AL.update_with_s_path(label4,deepcopy(skew4),skew_direction=1)

        e_idns = {13,16,17,18,19}
        c2w_map = {x:AL.K.weight_map[x] for x in e_idns}
        AL.reset_base(e_idns) 
        
        assert set(AL.K.weight_map.keys()) == e_idns 
        assert set(AL.K.base_elements) == e_idns 
        assert set(AL.pfgen.label_seq) == {"13","16","17","18","19"} 
        assert set(AL.I.label_seq) == e_idns 

        for x in e_idns: 
            q = AL.element_instability_vec(x)
            assert q == [c2w_map[x]] * 2 

if __name__ == '__main__':
    unittest.main()