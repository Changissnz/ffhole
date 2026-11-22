from automatons.false_claim_i import * 
from morebs2.numerical_generator import prg_to_prg__LCG_sequence__v2
import unittest

def sample_FalseClaimTypeI_DEBAT(constant_trust,form_type="P",trust=0.5,delta_mult=5.07,verbose=True):
    label_seq = ["a","bat","came","down","everyone","faked","highness"] 
    prg = prg = prg__LCG(324.52,4353.2,-1563.44,43449.65) 

    return FalseClaimTypeI.generate_instance(label_seq,form_type,delta_mult,\
        trust,prg,constant_trust=constant_trust,verbose=verbose) 

###
"""
py -m tests.test_false_claim_i
""" 
class FalseClaimTypeIMethods(unittest.TestCase):

    """
    demonstrates instability of claimant and subject over 
    100 iterations, where the `trust` variable remains constant 
    """ 
    def test__FalseClaimTypeI__next__case_1(self): 
        trust = 0.5 
        F = sample_FalseClaimTypeI_DEBAT(constant_trust=True,trust=trust,verbose=False) 

        for _ in range(100): 
            next(F) 
            assert F.trust == trust == 0.5, "got {}".format(F.trust)
        
        assert round(F.subject.cumulative_instability,5) == 513.66283 
        assert round(F.claimant.cumulative_instability,5) == 423.93711 

    """
    demonstrates perfect stability of subject in case of non-constant trust. 
    """
    def test__FalseClaimTypeI__next__case_2(self): 
        trust = 0.5 
        F = sample_FalseClaimTypeI_DEBAT(constant_trust=False,trust=trust,verbose=False) 

        t = F.trust 
        t_deltas = 0 
        for _ in range(100): 
            next(F) 
            t_deltas += int(F.trust != t)
            t = F.trust 

        assert t_deltas == 99         
        assert round(F.subject.cumulative_instability,5) == 0.0 
        assert round(F.claimant.cumulative_instability,5) == 2076.33693

    """
    demonstrates different instability scores from Case #1. The delta multiplier 
    for instability vectors is set to 1.57 here, instead of 5.07. 
    """
    def test__FalseClaimTypeI__next__case_3(self): 
        trust = 0.5 
        F = sample_FalseClaimTypeI_DEBAT(constant_trust=True,trust=trust,delta_mult=1.57,verbose=False) 

        for _ in range(100): 
            next(F) 
            assert F.trust == trust == 0.5, "got {}".format(F.trust)
        
        assert round(F.subject.cumulative_instability,5) == 20.0743 
        assert round(F.claimant.cumulative_instability,5) == 85.15915 

    """
    demonstrates a case of using G-form for derivable constituent composition, 
    instead of P-form, as in cases #1-3. 

    Delta multiplier for instability activatio is 10.57. 
    """
    def test__FalseClaimTypeI__next__case_4(self): 
        trust = 0.5 
        F = sample_FalseClaimTypeI_DEBAT(constant_trust=True,form_type="G",\
            trust=trust,delta_mult=10.57,verbose=False) 

        for _ in range(100): 
            next(F) 
            assert F.trust == trust == 0.5, "got {}".format(F.trust)
        
        assert round(F.subject.cumulative_instability,5) == 214.6171
        assert round(F.claimant.cumulative_instability,5) == 251.95232

if __name__ == '__main__':
    unittest.main()