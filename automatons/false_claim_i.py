from .false_claim_agents_i import * 

"""
(F)alse (C)laim Type (I)nterpretive. 
""" 
class FalseClaimTypeI: 

    def __init__(self,claimant:FCClaimantTypeI,subject:FCSubjectTypeI,\
        I:AGChainedLabelInterpreterTypeCEE,trust:float,prg): 

        assert type(claimant) == FCClaimantTypeI
        assert type(subject) == FCSubjectTypeI
        assert type(I) == AGChainedLabelInterpreterTypeCEE
        assert 0. <= trust <= 1.0 
        assert type(prg) in {MethodType,FunctionType}

        self.claimant = claimant
        self.subject = subject  
        self.I = I 
        self.trust = trust 
        self.prg = prg 
        return 

    def __next__(self): 
        label,skew_vec,skew_dir,no_cover = self.claimant.pose_claim(self.trust) 
        self.process_claim(label,skew_vec,skew_dir,no_cover) 

        process_instability
        return 

    def process_claim(self,label,skew_vec,skew_dir,no_cover):
        index = None 
        # case: add cover to the claim 
        if not no_cover: 
            self.I.update_with_s_path(label,skew_vec,skew_dir,add_to_chain=True) 
            index = len(self.I) - 2  
        else: 
            index = len(self.I) - 1

        V = self.I.s_path_instability_vec(index,label,skew_vec,skew_dir) 
        response = self.subject.respond_to_claim_(self.trust,not no_cover) 

        # case: subject accepts claim
        if response: 
            # instability goes to subject 
            if no_cover: 
                self.subject.add_ivec(V) 
            else: 
                self.claimant.add_ivec(V) 
        # case: subject does not accept claim 
        else: 
            # instability goes to claimant  
            self.claimant.add_ivec(V) 
        return 

    def process_instability(self): 
        self.subject.process_instability()
        self.claimant.process_instability()

        min_index = len(I) - 1

        # trust goes up when subject has instability 
        for x in self.subject.iv_cache: 
            min_index = min(x[0],min_index)
            self.trust_delta(True) 

        # trust goes up when claimant has instability 
        for x in self.claimant.iv_cache: 
            min_index = min(x[0],min_index)
            self.trust_delta(False)

        self.subject.clear_ivec_cache()
        self.claimant.clear_ivec_cache()

        self.revert_to_chain_link(min_index)
        return 

    def trust_delta(self,is_increase:bool): 
        q = prg_decimal(self.prg,[0.,1.]) 

        if is_increase: 
            q = q + 1.0 

        self.trust = self.trust * q 
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
        return FalseClaimTypeI(C,S,I,trust,prg) 