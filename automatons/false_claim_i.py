from .false_claim_agents_i import * 

"""
""" 
class FalseClaimTypeI: 

    def __init__(self,claimant:FCClaimantTypeI,subject:FCSubjectTypeI,\
        I:AGChainedLabelInterpreterTypeCEE,trust:float): 

        assert type(claimant) == FCClaimantTypeI
        assert type(subject) == FCSubjectTypeI
        assert type(I) == AGChainedLabelInterpreterTypeCEE
        assert 0. <= trust <= 1.0 

        self.claimant = claimant
        self.subject = subject  
        self.I = I 
        self.trust = trust 
        return 

    def __next__(self): 
        claim = self.claimant.pose_claim(self.trust) 
        return 

    def process_claim(self,label,skew_vec,skew_dir,no_cover):
        # case: add cover to the claim 
        if not no_cover: 
            self.I.update_with_s_path(label,skew_vec,skew_dir,add_to_chain=True) 

        response = self.subject.respond_to_claim_(self.trust,not no_cover) 
        return 

    def trust_delta(self): 
        return

    @staticmethod 
    def generate_instance(label_seq,form_type,delta_mult,act_ratio,trust,prg): 
        assert len(label_seq) == len(set(label_seq)) 
        assert len(label_seq) > 1 
        assert type(delta) in {int,float}

        c2w_map = {l:0. for l in label_seq} 
        cl_intrp = AGChainedLabelInterpreterTypeCEE(c2w_map,prg,form_type,maintain_constant_dim=True)

        num_lcgs = modulo_in_range(int(prg()),[3,7]) 
        claimant_prg = prg_to_LCG_stack(prg,num_lcgs,[add,sub,add]) 

        num_lcgs2 = modulo_in_range(int(prg()),[3,7]) 
        subject_prg = prg_to_LCG_stack(prg,num_lcgs2,[add,sub,add]) 

        iv_update_func = DEFAULT_FALSE_CLAIM_IVEC_DELTA_FUNCTION(delta_mult)
        iv_act_func = DEFAULT_FALSE_CLAIM_IVEC_ACTIVATION_FUNCTION(act_ratio)

        C = FCClaimantTypeI(cl_intrp.I,claimant_prg,iv_update_func,iv_act_func) 

        S = FCSubjectTypeI(cl_intrp.I,subject_prg,iv_update_func,iv_act_func) 
        return FalseClaimTypeI(C,S,I,trust)