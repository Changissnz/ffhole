from .false_claim_agents_ar import * 
from morebs2.numerical_generator import prg_to_LCG_stack,merge_two_prgs

DEFAULT_FALSE_CLAIM_TYPE_AR_MAX_ELEMENTS = 14  

class FalseClaimTypeAR: 

    def __init__(self,C:FCClaimantTypeAR,S:FCSubjectTypeI,I:AGChainedLabelInterpreterTypeCEE,\
        prg,verbose:bool=False): 

        assert type(C) == FCClaimantTypeAR
        assert type(S) == FCSubjectTypeAR
        assert type(I) == AGChainedLabelInterpreterTypeCEE
        assert type(prg) in {MethodType,FunctionType} 
        assert type(verbose) == bool 

        assert C.l_intrp.label_seq == S.l_intrp.label_seq 

        self.claimant = C 
        self.subject = S 
        self.I = I 
        self.prg = prg 
        self.verbose = verbose 

        # element idn -> (claimant control,subject control) [sums to 1.0]
        self.e2control_map = dict() 

        self.preproc() 
        return

    def preproc(self): 
        elements = self.I.current_elements() 
        self.limit_elements() 
        self.assign_control_to_elements(elements)
        return  

    #### TODO 
    def limit_elements(self): 
        elements = self.I.current_elements() 
        d = len(elements) - DEFAULT_FALSE_CLAIM_TYPE_AR_MAX_ELEMENTS

        if d > 0: 
            x = modulo_in_range(int(self.prg()),[4,int(DEFAULT_FALSE_CLAIM_TYPE_AR_MAX_ELEMENTS / 1.3)])
            prg_ = prg__single_to_int(self.prg)
            q = prg_choose_n(elements,x,prg_,is_unique_picker=True) 
            self.I.reset_base(set(q)) 
            self.claimant.l_intrp = self.I.I 
            self.subject.l_intrp = self.I.I 

    def assign_control_to_elements(self,elements:list): 
        assert type(elements) == list 

        prg_ = merge_two_prgs(self.prg,self.claimant.prg,add)
        prg_ = merge_two_prgs(prg_,self.subject.prg,sub)

        M_c = dict()
        M_s = dict()
        for q_ in elements: 
            d = round(float(prg_decimal(prg_,[0.,1.])),5) 
            M_c[q_] = d 
            M_s[q_] = 1. - d 

            self.e2control_map[q_] = (d,1. - d) 

        self.claimant.add_e2c_info(M_c) 
        self.subject.add_e2c_info(M_s)

        return

    def __next__(self): 

        M = self.claimant.pose_claim()
        M_ = deepcopy(M)
        for label,skew_vec in M_.items(): 
            self.I.update_with_s_path(label,skew_vec,skew_direction=1,add_to_chain=False) 

        M_ = self.claim_to_i2l_map(deepcopy(M)) 
        r = self.subject.respond_to_claim(M) 

        # case: subject takes action off of the claim 
        if r == 1: 
            self.process_claim_A(M_) 
        # case: subject reacts to the claim 
        else: 
            self.process_claim_R(M_) 

        self.limit_elements()
        self.process_instability()

    """
    converts a claim, a map of 
        element idn -> skew vector 
    to 
        element idn -> (index -> label set). 
    """
    def claim_to_i2l_map(self,M): 
        M_ = dict() 
        for k,v in M.items(): 
            p = self.I.I.label_to_s_path(k,v,1)
            M_[k] = self.I.I.path_to_lmap(p)
        return M_ 

    def process_claim_A(self,M): 
        if self.verbose: print("\t--- subject acts on claim")
        self.imbalance_from_claim(M)
        self.load_new_intrp(M) 
        self.exec_direct_paths(None)  
        return 

    def imbalance_from_claim(self,M): 
        elements = self.I.current_elements()
        length = len(elements) 

        ends_met = set() 
        for k,v in M.items(): 
            q = deepcopy(v[length-1]) 

            if len(q) != 1: continue 
            ends_met |= q 

        unmet_ends = sorted(set(elements) - ends_met) 
        self.add_instability_to_agents(unmet_ends)

        if self.verbose: 
            print("imbalance of ends={}".format(unmet_ends))
        return 

    def process_claim_R(self,M):
        elements = self.elements_from_claim_map(M,only_new_elements=True) 
        self.exec_direct_paths(elements) 
        return 

    def exec_direct_paths(self,elements): 
        self.exec_direct_paths_("subject",elements)
        self.exec_direct_paths_("claimant",elements) 
        return 

    def exec_direct_paths_(self,agent_idn:str,elements=None):
        assert agent_idn in {"subject","claimant"}
        assert type(elements) in {type(None),list,set}

        q = self.subject if agent_idn == "subject" else \
            self.claimant

        # case: default to the entire set of current interpreter's 
        #       elements.
        if type(elements) == type(None): 
            elements = self.I.current_elements()
        self.add_instability_to_agents(elements) 

    def control_of_element(self,element:int): 
        assert type(element) == int 

        if element in self.e2control_map: 
            return self.e2control_map[element] 

        x = self.I.label_to_constituents(element)

        c = [0,0] 
        for x_ in x: 
            q = self.e2control_map[x_]
            c[0] += q[0]
            c[1] += q[1] 
        
        self.e2control_map[element]  = (c[0] / len(x),c[1] / len(x)) 
        return self.e2control_map[element] 

    def load_new_intrp(self,M): 
        elements = self.elements_from_claim_map(M)
        elements = sorted(elements)
        L = LabelInterpreterTypeCEE(elements)
        self.I.add_link_v2(L)

        self.claimant.l_intrp = self.I.I 
        self.subject.l_intrp = self.I.I 
        return 

    def elements_from_claim_map(self,M,only_new_elements:bool=False):
        assert type(only_new_elements) == bool 

        elements = set(M.keys()) 
        for k,v in M.items(): 
            for k,v2 in v.items(): 
                i2 = self.I.constituents_to_label(v2)
                elements |= {i2} 

        if only_new_elements: 
            elements = elements - set(M.keys()) 
        return elements 

    def add_instability_to_agents(self,elements): 
        assert type(elements) in {set,list} 
        for x in elements: 
            cv,sv = self.element_instability_vectors(x) 
            self.claimant.add_ivec(cv,x) 
            self.subject.add_ivec(sv,x) 

    def process_instability(self): 
        self.subject.process_instability()
        self.claimant.process_instability()

    """
    return:
    - instability vector for claimant, instability vector for subject 
    """ 
    def element_instability_vectors(self,element): 
        q = self.I.element_instability_vec(element)
        q_ = np.array(q) 

        cc,sc = self.control_of_element(element) 
        return (1 - cc) * q_,(1 - sc) * q_


    @staticmethod 
    def generate_instance(label_seq,form_type,delta_mult,prg,claimant_rnp=(0.5,"control"),\
        subject_rnp=(0.5,"control"),verbose:bool=False): 

        assert len(label_seq) == len(set(label_seq)) 
        assert len(label_seq) > 1 
        assert type(delta_mult) in {int,float}

        c2w_map = {l:0. for l in label_seq} 
        cl_intrp = AGChainedLabelInterpreterTypeCEE(c2w_map,prg,form_type,maintain_constant_dim=True)

        num_lcgs = modulo_in_range(int(prg()),[3,7]) 
        claimant_prg = prg_to_LCG_stack(prg,num_lcgs,[add,sub,add]) 

        num_lcgs2 = modulo_in_range(int(prg()),[3,7]) 
        subject_prg = prg_to_LCG_stack(prg,num_lcgs2,[add,sub,add]) 

        iv_update_func = DEFAULT_FALSE_CLAIM_IVEC_DELTA_FUNCTION(delta_mult)
        iv_act_func = DEFAULT_FALSE_CLAIM_IVEC_ACTIVATION

        C = FCClaimantTypeAR(cl_intrp.I,claimant_prg,iv_update_func,iv_act_func,\
            claimant_rnp[0],claimant_rnp[1],verbose=verbose) 
        
        S = FCSubjectTypeAR(cl_intrp.I,subject_prg,iv_update_func,iv_act_func,\
            subject_rnp[0],subject_rnp[1],verbose=verbose) 
        return FalseClaimTypeAR(C,S,cl_intrp,prg,verbose) 