from .false_claim_agents_ar import * 
from morebs2.numerical_generator import prg_to_LCG_stack,merge_two_prgs

DEFAULT_FALSE_CLAIM_TYPE_AR_MAX_ELEMENTS = 14  

"""
agent_info_ratio := (r_0,r_1), r_i in [0.,1.]. Ratio values specify the number of instability and 
                control values over the elements the claimant and subject respectively have. 
"""
class FalseClaimTypeAR: 

    def __init__(self,C:FCClaimantTypeAR,S:FCSubjectTypeI,I:AGChainedLabelInterpreterTypeCEE,\
        agent_info_ratio,prg,verbose:int=0): 

        assert type(C) == FCClaimantTypeAR
        assert type(S) == FCSubjectTypeAR
        assert type(I) == AGChainedLabelInterpreterTypeCEE
        assert type(agent_info_ratio) == tuple and len(agent_info_ratio) == 2
        assert 0. <= agent_info_ratio[0] <= 1. and 0. <= agent_info_ratio[1] <= 1.
        assert type(prg) in {MethodType,FunctionType} 

        assert C.l_intrp.label_seq == S.l_intrp.label_seq 

        self.claimant = C 
        self.subject = S 
        self.I = I 
        self.agent_info_ratio = agent_info_ratio
        self.prg = prg 
        self.verbose = None  

        # element idn -> (claimant control,subject control) [sums to 1.0]
        self.e2control_map = dict() 

        self.preproc(verbose) 
        return

    #-------------------------------------- preprocessing methods 

    def preproc(self,verbosity): 
        elements = self.I.current_elements() 
        self.limit_elements() 
        self.assign_control_to_elements(elements)

        self.assign_info_to_agents(set(elements),"claimant","instability") 
        self.assign_info_to_agents(set(elements),"subject","instability") 
        self.assign_info_to_agents(set(elements),"claimant","control") 
        self.assign_info_to_agents(set(elements),"subject","control") 

        self.set_verbosity(verbosity) 
        return

    def assign_control_to_elements(self,elements:list): 
        assert type(elements) == list 

        prg_ = self.tri_prng() 

        M_c = dict()
        M_s = dict()
        for q_ in elements: 
            d = round(float(prg_decimal(prg_,[0.,1.])),5) 
            M_c[q_] = d 
            M_s[q_] = 1. - d 

            self.e2control_map[q_] = (d,1. - d) 

        return

    def set_verbosity(self,verbosity): 
        assert type(verbosity) == int and verbosity in {0,1,2}, "got {}".format(verbosity)
        self.verbose = verbosity 
        self.claimant.verbose = bool(verbosity)
        self.subject.verbose = bool(verbosity) 

    #-------------------------------------------------------------------- 

    """
    main method 
    """
    def __next__(self): 

        if self.verbose: 
            print("\t\t--------------------")
            num_elements = len(self.I.current_elements())
            print("** claimant knowledge for {} elements".format(num_elements))
            print("control: {}, instability: {}\n".format(len(self.claimant.e2control_map),\
                len(self.claimant.i2i_map)))

            print("** subject knowledge for {} elements".format(num_elements)) 
            print("control: {}, instability: {}\n".format(len(self.subject.e2control_map),\
                len(self.subject.i2i_map)))
            print("\t\t=====================")

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

        self.process_instability()
        self.limit_elements()

    #-------------------------------------------- processing actions from and reactions to claim 

    def process_claim_A(self,M): 
        if self.verbose: print("\t--- subject acts on claim")
        self.imbalance_from_claim(M)
        self.load_new_intrp(M) 
        self.exec_direct_paths(None)  
        return 

    def process_claim_R(self,M):
        if self.verbose: print("\t--- subject reacts to claim")
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

    #---------------------------------------------------------------------------

    def limit_elements(self): 
        elements = self.I.current_elements() 
        d = len(elements) - DEFAULT_FALSE_CLAIM_TYPE_AR_MAX_ELEMENTS

        q = set(elements) 
        if d > 0: 
            prg_ = prg__single_to_int(self.tri_prng())
            x = modulo_in_range(prg_(),[4,int(DEFAULT_FALSE_CLAIM_TYPE_AR_MAX_ELEMENTS / 1.3)])
            q = set(prg_choose_n(elements,x,prg_,is_unique_picker=True)) 
            self.I.reset_base(q) 
            self.claimant.l_intrp = self.I.I 
            self.subject.l_intrp = self.I.I 

        self.claimant.filter_elements(q)
        self.subject.filter_elements(q)

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

    #----------------------------------------- for updating agent database + interpreter 

    """
    updates the agent database of instability and control values for 
    `claimant` and `subject`. 
    """
    def update_agent_db(self,elements):
        unstable_elements = set() 
        control_elements = set() 

        for x in elements: 
            stat_i = not (self.claimant.knows_instability(x) and self.subject.knows_instability(x)) 
            stat_c = not (self.claimant.knows_control(x) and self.subject.knows_control(x)) 

            if stat_i: 
                unstable_elements |= {x} 
            
            if stat_c:
                control_elements |= {x} 
    
        self.assign_info_to_agents(unstable_elements,"claimant","instability") 
        self.assign_info_to_agents(unstable_elements,"subject","instability") 
        self.assign_info_to_agents(control_elements,"claimant","control") 
        self.assign_info_to_agents(control_elements,"subject","control") 
        return 

    def assign_info_to_agents(self,elements:set,agent_idn:str,info_type:str): 
        
        assert agent_idn in {"claimant","subject"}
        assert info_type in DEFAULT_FALSE_CLAIM_PFUNCTION_MAP

        # choose the elements to send info to `agent_idn`        
        l = ceil(self.agent_info_ratio[0] * len(elements)) 
        q0 = []  
        if l > 0: 
            prg_ = prg__single_to_int(self.prg)
            q0 = prg_choose_n(sorted(elements),l,prg_,is_unique_picker=True) 

        ##print("ASSIGNING {} / {}".format(len(elements),l))

        # determine the appropriate function 
        F = None 
        index = 0 if agent_idn == "claimant" else 1 
        if info_type == "control": 
            F = lambda x: self.control_of_element(x)[index]
        else: 
            F = lambda x: round(float(np.sum(self.element_instability_vectors(x)[index])),5) 

        D = {q_:F(q_) for q_ in q0} 
        ##print("DX: ",D)
        A = self.claimant if agent_idn == "claimant" else \
            self.subject
        A.add_info(D,info_type) 
        return 

    def load_new_intrp(self,M): 
        elements = self.elements_from_claim_map(M)
        elements = sorted(elements)
        L = LabelInterpreterTypeCEE(elements)
        self.I.add_link_v2(L)

        self.claimant.l_intrp = self.I.I 
        self.subject.l_intrp = self.I.I 
        return 

    #---------------------------------------- instability calculations 

    def add_instability_to_agents(self,elements): 
        assert type(elements) in {set,list} 

        for x in elements: 
            cv,sv = self.element_instability_vectors(x) 
            self.claimant.add_ivec(cv)#,x) 
            self.subject.add_ivec(sv)#,x) 

        self.update_agent_db(elements) 

    def process_instability(self):
        self.subject.verbose = bool(self.verbose == 2)
        self.claimant.verbose = bool(self.verbose == 2)

        self.subject.process_instability()
        self.claimant.process_instability()

        self.subject.verbose = bool(self.verbose)
        self.claimant.verbose = bool(self.verbose)

    """
    return:
    - instability vector for claimant, instability vector for subject 
    """ 
    def element_instability_vectors(self,element): 
        q = self.I.element_instability_vec(element)
        q_ = np.array(q) 

        cc,sc = self.control_of_element(element) 
        return (1 - cc) * q_,(1 - sc) * q_

    """
    calculates the `control` of a new `element` for 
    both `claimant` and `subject`, by averaging the 
    control of the `element`'s constituents by 
    the `claimant` and `subject`. 
    """
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

    #----------------------------------------------------------------------

    def tri_prng(self): 
        prg_ = merge_two_prgs(self.prg,self.claimant.prg,add)
        return merge_two_prgs(prg_,self.subject.prg,sub)
    

    @staticmethod 
    def generate_instance(label_seq,form_type,delta_mult,prg,\
        claimant_info_ratio,subject_info_ratio,claimant_rnp=(0.5,"control"),\
        subject_rnp=(0.5,"control"),verbose:int=0): 

        assert len(label_seq) == len(set(label_seq)) 
        assert len(label_seq) > 1 
        assert type(delta_mult) in {int,float}
        assert verbose in {0,1,2}

        c2w_map = {l:0. for l in label_seq} 
        cl_intrp = AGChainedLabelInterpreterTypeCEE(c2w_map,prg,form_type,maintain_constant_dim=True)

        num_lcgs = modulo_in_range(int(prg()),[3,7]) 
        claimant_prg = prg_to_LCG_stack(prg,num_lcgs,[add,sub,add]) 

        num_lcgs2 = modulo_in_range(int(prg()),[3,7]) 
        subject_prg = prg_to_LCG_stack(prg,num_lcgs2,[add,sub,add]) 

        iv_update_func = DEFAULT_FALSE_CLAIM_IVEC_DELTA_FUNCTION(delta_mult)
        iv_act_func = DEFAULT_FALSE_CLAIM_IVEC_ACTIVATION

        C = FCClaimantTypeAR(cl_intrp.I,claimant_prg,iv_update_func,iv_act_func,\
            claimant_rnp[0],claimant_rnp[1],verbose=bool(verbose)) 
        
        S = FCSubjectTypeAR(cl_intrp.I,subject_prg,iv_update_func,iv_act_func,\
            subject_rnp[0],subject_rnp[1],verbose=bool(verbose)) 
        ##print("Q: ",C)
        return FalseClaimTypeAR(C,S,cl_intrp,(claimant_info_ratio,subject_info_ratio),\
            prg,verbose) 