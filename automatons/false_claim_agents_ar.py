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
"""
def path_score_to_singleton__FCTAR(pscore,risk_aversion):
    assert 0. <= risk_aversion <= 1. 
    assert type(pscore[2]) == type(pscore[1]) == int 
    assert pscore[2] > 0 
    assert 0. <= pscore[0] <= pscore[2] 

    risk = 1.0 - risk_aversion

    x = pscore[0] + (pscore[1] * risk)
    return x / pscore[2] 

"""
The claimant agent in False Claim Type (A)ction-(R)elational. 

A claim, in False Claim Type AR, is a map of the form 
    label -> <sequence of elements (column index,index shift)>. 
All labels of the current `LabelInterpreterTypeCEE` are present in 
the map. 
""" 
class FCClaimantTypeAR(FCAgent):

    def __init__(self,l_intrp:LabelInterpreterTypeCEE,prg,iv_update_func,iv_act_func,risk_aversion:float,\
        verbose:bool=False):

        assert 0. <= risk_aversion <= 1.0 

        super().__init__(l_intrp,prg,iv_update_func,iv_act_func,verbose) 
        self.idn = "claimant"  
        self.pending_claim = None 

        self.risk_aversion = risk_aversion
        # integer label -> r in [0.,1.]
        self.e2control_map = dict() 
        return 

    def add_e2c_info(self,M): 
        assert type(M) == dict 
        self.e2control_map.update(M) 

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
            q2 = self.predict_path_control(label,q)
            s = path_score_to_singleton__FCTAR(q2,self.risk_aversion)

            path_scores.append((q,s)) 

        path_scores = prg_seqsort_ties(path_scores,self.prg,vf=lambda x:x[1])
        return path_scores[-1][0] 

    #-------------------------------- methods used by agent to generate S-paths of 
    #-------------------------------- highest predicted control over 

    def generate_s_path_(self): 
        l = len(self.l_intrp.label_seq)

        skew_vec = [] 
        for i in range(1,l-1):  
            index_skew = modulo_in_range(int(self.prg()),[1,l]) 
            skew_vec.append((i,index_skew)) 
        return skew_vec 

    """
    return:
    - [0] control score (cumulative weights of known), 
      [1] number of unknown, 
      [2] number total. 
    """
    def predict_path_control(self,label,skew_vec): 
        P = self.l_intrp.label_to_s_path(label,skew_vec,skew_direction=1)
        M = self.l_intrp.path_to_lmap(P)

        unknowns = 0 
        c = 0. 

        for k,v in M.items(): 
            q = self.control_of_element(v) 

            if type(q) == type(None): 
                unknowns += 1 
                continue 
            c += q 
        
        return c,unknowns,len(M) 
                
    def control_of_element(self,element:set):  
        assert type(element) == set and len(element) > 0 

        c = 0. 
        for x in element: 
            if x not in self.e2control_map: return None 
            c += self.e2control_map[x] 
        return c / len(element) 

    #--------------------------------------------------------------------


class FCSubjectTypeAR(FCAgent): 

    def __init__(self,l_intrp:LabelInterpreterTypeCEE,prg,iv_update_func,iv_act_func,verbose:bool=False):

        super().__init__(l_intrp,prg,iv_update_func,iv_act_func,verbose) 

        self.idn = "subject" 

        self.risk_aversion = risk_aversion
        # integer label -> r in [0.,1.]
        self.e2control_map = dict() 

        # stores most recent boolean response to 
        # most recent claim from <FCClaimantTypeI> 
        self.accepts = None 
        return 

    def predict_reaction_control(self,claim_map): 

        return -1 

    def respond_to_claim(self,claim_map:dict):
        assert type(claim_map) == dict 