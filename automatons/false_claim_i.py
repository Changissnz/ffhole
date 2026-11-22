from .false_claim_agents_i import * 
from morebs2.numerical_generator import prg_to_LCG_stack

DEFAULT_FALSE_CLAIM_RESET_INTERVAL = 5

"""
(F)alse (C)laim Type (I)nterpretive. 
""" 
class FalseClaimTypeI: 

    def __init__(self,claimant:FCClaimantTypeI,subject:FCSubjectTypeI,\
        I:AGChainedLabelInterpreterTypeCEE,trust:float,prg,constant_trust:bool,verbose:bool=False): 

        assert type(claimant) == FCClaimantTypeI
        assert type(subject) == FCSubjectTypeI
        assert type(I) == AGChainedLabelInterpreterTypeCEE
        assert 0. <= trust <= 1.0 
        assert type(prg) in {MethodType,FunctionType}
        assert type(constant_trust) == bool  

        self.claimant = claimant
        self.subject = subject  
        self.I = I 
        self.I_ = deepcopy(I)
        self.trust = trust 
        self.prg = prg 
        self.constant_trust = constant_trust
        self.verbose = None
        self.set_verbosity(verbose)  
        return 

    def set_verbosity(self,verbose:bool): 
        assert type(verbose) == bool 
        self.claimant.verbose = verbose 
        self.subject.verbose = verbose 

    def __next__(self): 
        label,skew_vec,skew_dir,no_cover = self.claimant.pose_claim(self.trust) 
        self.process_claim(label,skew_vec,skew_dir,no_cover) 
        self.process_instability()

        self.subject.increment_timestamp()
        self.claimant.increment_timestamp()

        self.reset_intrp()
        return 

    def reset_intrp(self): 
        if not (self.subject.timestamp % DEFAULT_FALSE_CLAIM_RESET_INTERVAL == 0 \
            and self.subject.timestamp > 0): return 

        self.I = deepcopy(self.I_) 
        self.load_new_intrp() 

    def process_claim(self,label,skew_vec,skew_dir,no_cover):
        index = len(self.I) - 1
        self.I.update_with_s_path(label,skew_vec,skew_dir,add_to_chain=True) 

        V = self.I.s_path_instability_vec(index,label,deepcopy(skew_vec),skew_dir) 
        response = self.subject.respond_to_claim_(self.trust,not no_cover) 

        # case: subject accepts claim
        if response:             
            # instability goes to subject 
            if no_cover: 
                self.subject.add_ivec(V) 
            else:
                self.claimant.add_ivec(V) 
            ##self.subject.add_ivec(deepcopy(V))
        # case: subject does not accept claim 
        else: 
            # instability goes to claimant  
            self.claimant.add_ivec(V) 
            self.I.revert_to_chain_link(len(self.I) - 2) 
        self.load_new_intrp() 
        return 

    def process_instability(self): 
        self.subject.process_instability()
        self.claimant.process_instability()

        min_index = len(self.I) - 1

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

        try: 
            self.I.revert_to_chain_link(min_index)
        except: 
            pass 

        self.load_new_intrp() 
        return 

    def load_new_intrp(self): 
        self.claimant.l_intrp = self.I.I 
        self.subject.l_intrp = self.I.I 

    def trust_delta(self,is_increase:bool): 
        if self.constant_trust: return 

        q = prg_decimal(self.prg,[0.,1.]) 

        if is_increase: 
            q = q + 1.0 

        self.trust = min([1.0,self.trust * q]) 
        return 

    @staticmethod 
    def generate_instance(label_seq,form_type,delta_mult,act_ratio,trust,prg,constant_trust:bool=True,verbose:bool=False): 
        assert len(label_seq) == len(set(label_seq)) 
        assert len(label_seq) > 1 
        assert type(delta_mult) in {int,float}
        assert 0. <= trust <= 1.

        c2w_map = {l:0. for l in label_seq} 
        cl_intrp = AGChainedLabelInterpreterTypeCEE(c2w_map,prg,form_type,maintain_constant_dim=True)

        num_lcgs = modulo_in_range(int(prg()),[3,7]) 
        claimant_prg = prg_to_LCG_stack(prg,num_lcgs,[add,sub,add]) 

        num_lcgs2 = modulo_in_range(int(prg()),[3,7]) 
        subject_prg = prg_to_LCG_stack(prg,num_lcgs2,[add,sub,add]) 

        iv_update_func = DEFAULT_FALSE_CLAIM_IVEC_DELTA_FUNCTION(delta_mult)
        iv_act_func = DEFAULT_FALSE_CLAIM_IVEC_ACTIVATION

        C = FCClaimantTypeI(cl_intrp.I,claimant_prg,iv_update_func,iv_act_func) 

        S = FCSubjectTypeI(cl_intrp.I,subject_prg,iv_update_func,iv_act_func) 
        return FalseClaimTypeI(C,S,cl_intrp,trust,prg,constant_trust,verbose) 