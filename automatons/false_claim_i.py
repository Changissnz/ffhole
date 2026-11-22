from .false_claim_agents_i import * 
from morebs2.numerical_generator import prg_to_LCG_stack

DEFAULT_FALSE_CLAIM_RESET_INTERVAL = 5

"""
(F)alse (C)laim Type (I)nterpretive. 

Automaton consists of two agents, a `claimant` and a `subject`, where 
the `claimant` poses a claim to the `subject` at every timestamp. 

The matter that the activity of claiming revolves around an initial 
sequence of details D. The structure, <LabelInterpreterTypeCEE>, 
is used to represent these details D, as a square lattice of dimension 
|D| x |D|. In the perfect case of accuracy, an agent maps every detail 
along its direct path in this <LabelInterpreterTypeCEE>. 

The structure <AGChainedLabelInterpreterTypeCEE> is used to operate 
the initial <LabelInterpreterTypeCEE>, in a chain-like manner. 
NOTE: see file<falses.label_intrp> and file<falses.chained_label_intrp>
      for more details on these operations. 
<AGChainedLabelInterpreterTypeCEE> adds a new <LabelInterpreterTypeCEE> 
to its chain of <LabelInterpreterTypeCEE>, every time the `subject` and 
`claimant` agree on a new claim made from these details D' := delta(D). 
This chain of interpreters therefore represents the examination process 
of an initial matter, a sequence of details D, that is transformed from 
D based on the claims made from `claimant` to `subject`. 

-------------------------------------------------------------------------
At any timestamp, both the `subject` and the `claimant` act on the same 
<LabelInterpreter>.

At every timestamp, the `claimant` first poses a claim to the subject. The 
claim is in the form of:
- a label (detail) on the <LabelInterpreterTypeCEE>, 
- a sequence of skews (column index, index shift) for the interpreter's traversal. 

      explanatory
    ---------------
A claim, in this representation, is fallacious because of the non-null skew, 
which results in an indirect path from one detail to its effect (an end node 
of the square lattice graph). A fallacy at a column index results in a multi-label 
(morphism of details) into a new detail (termed "element" by the kernel). 

A claim is associated with an instability vector, which is calculated by the 
kernel, <KernelReprTypeDCCWSM>, of the <AGChainedLabelInterpreterTypeCEE>. 

NOTE: the default generation method, <FalseClaimTypeI.generate_instance>, sets the 
      instability for all base elements at 0. 
    -----------------

Additionally, the `claimant` has the option to add a "cover" over this claim. When 
a "cover" is added, the `subject` will always accept the claim. Otherwise, the 
`subject` accepts the claim iff its PRNG output falls below the `trust`.

If the `subject` accepts a claim not covered by the `claimant`, the subject receives 
the claim's associated instability vector. If the claim is covered, the `claimant` 
receives said instability vector. 

If the `subject` does not accept the claim, the `claimant` receives the instability 
vector. 

If the claim is accepted, both agents use the <LabelInterpreterTypeCEE> updated with 
the skew path of the claim. 
-----------------------------------------------------------------------------------

By the default functions (see file<automatons.false_claim_agents_i>), any instability 
vector w/ at least one non-zero element will eventually be activated, once all 
non-zero elements are at least 1.0 in value. When the instability vector activates, 
the summation of the vector's original values is added to the instability of the agent 
in possession of it. 

Activated instability vectors determine the <LabelInterpreterTypeCEE> that the `subject` 
and `claimant` uses. At any timestamp, the <LabelInterpreterTypeCEE> used is the one 
at the minimum index of an instability vector, belonging to either the `subject` or 
the `claimant`, that activated at the end of the previous timestamp. 
NOTE: see method<FalseClaimTypeI.process_instability>. 

NOTE: due to the explosive growth in computing instability over multiple links of the 
<AGChainedLabelInterpreterTypeCEE>, the default is for the chain of <LabelInterpreterTypeCEE>s 
to reset back to the original for every DEFAULT_FALSE_CLAIM_RESET_INTERVAL timestamps. 
NOTE: the reset from DEFAULT_FALSE_CLAIM_RESET_INTERVAL will sometimes cause associated 
<LabelInterpreterTypeCEE>s from instability vectors to not be present during those 
vectors' activations.
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

        self.intrp_resets = 0 
        return 

    def set_prg(self,agent:str,prg):
        assert agent in {"claimant","subject","intermediary"} 
        assert type(prg) in {MethodType,FunctionType}

        if agent == "claimant": 
            self.claimant.prg = prg 
        elif agent == "subject": 
            self.subject.prg = prg 
        else: 
            self.prg = prg 

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

        self.subject.reset_timestamp()
        self.claimant.reset_timestamp() 

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
        min_index_ = len(self.I) - 1 

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

            stat = min_index == min_index_
            self.intrp_resets += int(stat)

            if self.verbose and stat: print("interpreter resets to {}".format(min_index))
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
    def generate_instance(label_seq,form_type,delta_mult,trust,prg,constant_trust:bool=True,verbose:bool=False): 
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