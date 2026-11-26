from .false_claim_agents_i import * 

DEFAULT_FALSE_CLAIM_TYPE_AR_CLAIM_NUM_PATH_ATTEMPTS = 4 

"""
function specially allocated for False Claim Type AR. 

Converts a path score, consisting of 
[0] control score (cumulative weights of known), 
[1] number of unknown, 
[2] number total, 

to a float in [0.,1.], in consideration of `risk_aversion`, 
a variable such that (1 - `risk_aversion`) is the weight 
assigned to unknowns. 

Used for gauging agent "control" over an element, based on 
`pscore`. 
"""
def path_score_to_singleton__FCTAR(pscore,risk_aversion):
    assert 0. <= risk_aversion <= 1. 
    assert type(pscore[2]) == type(pscore[1]) == int 
    assert pscore[2] >= 0 
    assert 0. <= pscore[0] <= pscore[2] 

    # case: no elements, full control. 
    if pscore[2] == 0: return 1 

    risk = 1.0 - risk_aversion

    x = pscore[0] + (pscore[1] * risk)
    return x / pscore[2] 

"""
similar to the above function, except substitutes unknown values 
with the `mean_value`, based on a proportion mapped from `risk_aversion`. 
"""
def path_score_to_singleton_type_MS__FCTAR(pscore,mean_value,risk_aversion):
    assert 0. <= risk_aversion <= 1. 
    assert type(pscore[2]) == type(pscore[1]) == int 
    assert pscore[2] >= pscore[1] >= 0 
    assert 0. <= pscore[0]

    # case: no elements, no instability 
    if pscore[2] == 0: 
        return 0. 

    risk = 1.0 - risk_aversion
    return pscore[0] + (pscore[1] * risk * mean_value) 

# prediction function map 
DEFAULT_FALSE_CLAIM_PFUNCTION_MAP = {"control":path_score_to_singleton__FCTAR,\
    "instability":path_score_to_singleton_type_MS__FCTAR}

#--------------------------------------------------------------------------------------

class FCAgentTypeAR(FCAgent):

    def __init__(self,l_intrp:LabelInterpreterTypeCEE,prg,iv_update_func,iv_act_func,risk_aversion:float,\
        prediction_type:str,verbose:bool=False):
        assert 0. <= risk_aversion <= 1.0 
        assert prediction_type in DEFAULT_FALSE_CLAIM_PFUNCTION_MAP

        super().__init__(l_intrp,prg,iv_update_func,iv_act_func,verbose) 
        
        self.risk_aversion = risk_aversion
        self.ptype = prediction_type

        # integer label -> r in [0.,1.]
        self.e2control_map = dict() 

        # integer label -> cumulative instability 
        self.i2i_map = dict() 

        self.mean_known_instability = 0.0 

    def add_e2c_info(self,M): 
        assert type(M) == dict 
        self.e2control_map.update(M) 

    def add_ivec(self,V,element_idn): 
        assert type(V) == list or is_vector(V) 
        assert 0.0 <= np.min(V) <= np.max(V) <= 1.0 
        assert type(element_idn) == int

        assert cumulative_instability >= 0. and is_number(cumulative_instability)
        self.iv_queue.append((self.timestamp,deepcopy(V),deepcopy(V),element_idn)) 

        # case: element already logged (assumes all instability vectors from 
        #       element_idn start at the same value). 
        if element_idn in self.i2i_map: 
            return 

        self.i2i_map[element_idn] = float(sum(V))
        self.mean_known_instability = (self.mean_known_instability + \
            self.i2i_map[element_idn]) / len(self.i2i_map)

    """
    If `only_new_elements` is set to True, only considers column indices 
    that are multi-labels. 

    return:
    - [0] control|instability score (cumulative weights of known), 
      [1] number of unknown, 
      [2] number total. 
    """
    def predict_path_score(self,label,skew_vec,only_new_elements:bool): 
        
        def flter(v): 
            if only_new_elements and len(v) == 1: 
                return False 
            return True  

        P = self.l_intrp.label_to_s_path(label,skew_vec,skew_direction=1)
        M = self.l_intrp.path_to_lmap(P)

        num_elements = 0 
        unknowns = 0 
        c = 0. 

        for k,v in M.items(): 
            stat = flter(v) 
            if not stat: continue 

            q = self.element_to_value(v,self.ptype) 
            num_elements += 1 

            if type(q) == type(None): 
                unknowns += 1 
                continue 
            c += q 
        
        return c,unknowns,num_elements  

    def condense_path_score(self,pscore):
        F = DEFAULT_FALSE_CLAIM_PFUNCTION_MAP[self.ptype] 
        if self.ptype == "control": 
            return F(pscore,self.risk_aversion)
        return F(pscore,self.mean_known_instability,self.risk_aversion)

    def element_to_value(self,element:set,ptype:str):  
        assert type(element) == set and len(element) > 0 
        assert ptype in DEFAULT_FALSE_CLAIM_PFUNCTION_MAP

        c = 0. 

        if ptype == "control": 
            D = self.e2control_map
            denominator = len(element) 
        else: 
            D = self.i2i_map
            denominator = 1

        for x in element: 
            if x not in D: return None 
            c += D[x] 
        return c / denominator


"""
The claimant agent in False Claim Type (A)ction-(R)elational. 

A claim, in False Claim Type AR, is a map of the form 
    label -> <sequence of elements (column index,index shift)>. 
All labels of the current `LabelInterpreterTypeCEE` are present in 
the map. 
""" 
class FCClaimantTypeAR(FCAgentTypeAR):

    def __init__(self,l_intrp:LabelInterpreterTypeCEE,prg,iv_update_func,iv_act_func,risk_aversion:float,\
        prediction_type:str,verbose:bool=False):

        super().__init__(l_intrp,prg,iv_update_func,iv_act_func,risk_aversion,prediction_type,verbose) 
        self.idn = "claimant"  
        self.pending_claim = None 
        return 

    def pose_claim(self): 
        self.pending_claim = self.make_claim() 
        if self.verbose: 
            print("{} makes claim with {} of paths".format(self.idn,len(self.pending_claim)))
            print() 

        return self.pending_claim

    def make_claim(self): 
        M = {}
        for label in self.l_intrp.label_seq: 
            skew_vec = self.generate_s_path()
            M[label] = skew_vec
        return M 

    def generate_s_path(self,label): 

        path_scores = [] 
        for _ in range(DEFAULT_FALSE_CLAIM_TYPE_AR_CLAIM_NUM_PATH_ATTEMPTS):
            q = self.generate_s_path_()
            q2 = self.predict_path_score(label,q,False)
            s = self.condense_path_score(q2)

            path_scores.append((q,s)) 

        path_scores = prg_seqsort_ties(path_scores,self.prg,vf=lambda x:x[1])

        index = 0 if self.ptype == "instability" else -1
        return path_scores[index][0] 

    #-------------------------------- methods used by agent to generate S-paths of 
    #-------------------------------- highest predicted control|lowest instability 

    def generate_s_path_(self): 
        l = len(self.l_intrp.label_seq)

        skew_vec = [] 
        for i in range(1,l-1):  
            index_skew = modulo_in_range(int(self.prg()),[1,l]) 
            skew_vec.append((i,index_skew)) 
        return skew_vec 

    #--------------------------------------------------------------------

"""
The subject agent in False Claim Type (A)ction-(R)elational. 

A claim, in False Claim Type AR, is a map of the form 
    label -> <sequence of elements (column index,index shift)>. 
All labels of the current `LabelInterpreterTypeCEE` are present in 
the map. 
""" 
class FCSubjectTypeAR(FCAgent): 

    def __init__(self,l_intrp:LabelInterpreterTypeCEE,prg,iv_update_func,iv_act_func,risk_aversion:float,\
        prediction_type:str,verbose:bool=False):

        super().__init__(l_intrp,prg,iv_update_func,iv_act_func,risk_aversion,prediction_type,verbose) 
        self.idn = "subject" 

        # stores most recent boolean response to 
        # most recent claim from <FCClaimantTypeI> 
        self.accepts = None 

        # 1 for action, -1 for reaction 
        self.action_sequence = [] 
        return 

    def predict_R_effect(self,claim_map):
        assert type(claim_map) == dict 
        assert type(is_reaction) == bool  

        x = [0,0,0]
        for l,skew_vec in claim_map.items(): 
            q = self.predict_path_score(l,skew_vec,only_new_elements=True) 
            x[0] += q[0]
            x[1] += q[1]
            x[2] += q[2]
        return self.condense_path_score(tuple(x))

    def predict_A_effect(self,claim_map):
        unique_elements = [{l} for l in self.l_intrp.label_seq] 

        for label,skew_vec in claim_map.items(): 
            P = self.l_intrp.label_to_s_path(label,skew_vec,skew_direction=1)
            M = self.l_intrp.path_to_lmap(P)

            for v in M.values(): 
                if v not in unique_elements: 
                    unique_elements.append(v) 

        v = 0 
        num_unknown = 0 
        for element in unique_elements:
            v_ = self.element_to_value(element,self.ptype)

            if type(v_) == type(None): 
                num_unknown += 1 
                continue 
            v += v_ 
        
        x = (v,num_unknown,len(unique_elements))
        return self.condense_path_score(x)

    def respond_to_claim(self,claim_map:dict):
        assert type(claim_map) == dict 

        r = self.predict_R_effect(claim_map) 
        a = self.predict_A_effect(claim_map) 

        d = prg_decimal(self.prg,[0.,1.])         
        q = -1 if r >= a else 1 

        # take risk, do the opposite 
        if d >= self.risk_aversion: 
            q = q * -1 
        
        self.action_sequence.append(q) 
        return q 