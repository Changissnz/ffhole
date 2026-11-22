from falses.chained_label_intrp import * 

def DEFAULT_FALSE_CLAIM_IVEC_DELTA_FUNCTION(multiplier):
    assert multiplier > 1.0 

    def f(V): 
        return list(np.array(V) * multiplier) 

    return f 

def DEFAULT_FALSE_CLAIM_IVEC_ACTIVATION_FUNCTION(min_ratio): 
    assert 0.0 <= min_ratio <= 1.0
    
    def f(V): 
        q = np.where(np.array(V) >= 1.0)[0] 
        return len(q) >= min_ratio * len(V) 

    return f 

"""
(F)alse (C)laim Agent Type (I)nterpretive. 

l_intrp := <LabelInterpreterTypeCEE>, the square-lattice interpreter for  
        choices (labels). 
prg := function|method, PRNG used for making decisions. 
iv_update_func := function|method, f(V) -> (V',?is activated?).
iv_act_func := function|method, f(V) -> non-negative float. 
"""
class FCAgentTypeI: 

    def __init__(self,l_intrp:LabelInterpreterTypeCEE,prg,iv_update_func,iv_act_func):
        assert type(l_intrp) == LabelInterpreterTypeCEE
        assert len(l_intrp) > 1 
        assert type(prg) in {MethodType,FunctionType} 
        assert type(iv_update_func) in {MethodType,FunctionType} 
        assert type(iv_act_func) in {MethodType,FunctionType} 

        self.l_intrp = l_intrp
        self.prev_intrps = deque() 

        self.prg = prg 
        self.iv_ufunc = iv_update_func
        self.iv_afunc = iv_act_func

        self.iv_queue = deque() 
        self.iv_cache = deque() 

        self.cumulative_instability = 0.0 

        self.timestamp = 0 
        return 

    def update_label_intrp(self,l_intrp): 
        self.prev_intrps.append(deepcopy(self.l_intrp)) 
        self.l_intrp = l_intrp
        return 

    def add_ivec(self,V): 
        assert type(V) == list or is_vector(V) 
        assert 0.0 <= np.min(V) <= np.max(V) <= 1.0 
        self.iv_queue.append((self.timestamp,deepcopy(V),deepcopy(V))) 

    def process_instability(self): 
        Q2 = deque() 

        while len(self.iv_queue) > 0: 
            t,iv,iv_ = self.iv_queue.popleft() 

            new_v,stat = self.iv_ufunc(iv_) 

            if stat: 
                self.iv_cache.append(iv)
                q = self.iv_afunc(iv) 
                self.cumulative_instability += q 
            else: 
                Q2.append((iv,iv_)) 
        self.iv_queue = Q2 
        return  

    def increment_timestamp(self): 
        self.timestamp += 1 

"""
The subject agent in False Claim Type Interpretive. 
"""
class FCSubjectTypeI(FCAgentTypeI): 

    def __init__(self,l_intrp:LabelInterpreterTypeCEE,prg,iv_update_func,iv_act_func):

        super().__init__(l_intrp,prg,iv_update_func,iv_act_func) 

        # stores most recent boolean response to 
        # most recent claim from <FCClaimantTypeI> 
        self.accepts = None 
        return 

    def respond_to_claim_(self,trust:float,claim_is_covered:bool): 

        # case: claim has been covered, default to `accept`
        if claim_is_covered: 
            return True 

        q = prg_decimal(self.prg,[0.,1.]) 

        # case: PRNG satisfies trust threshold
        self.accepts = q < trust
        return self.accepts 

class FCClaimantTypeI(FCAgentTypeI):

    def __init__(self,l_intrp:LabelInterpreterTypeCEE,prg,iv_update_func,iv_act_func):
        super().__init__(l_intrp,prg,iv_update_func,iv_act_func) 

        self.pending_claim = None 
        return 

    def pose_claim(self,trust:float): 

        label,skew_vec,skew_dir = self.make_claim() 
        q = prg_decimal(self.prg,[0.,1.]) 
        no_cover = q < trust
        self.pending_claim = label,skew_vec,skew_dir,no_cover 

        return self.pending_claim

    def make_claim(self): 
        # choose a label 
        l = len(self.l_intrp.label_seq)
        i = int(self.prg()) % l
        label = self.l_intrp.label_seq[i] 

        # calculate skew 
        skew_vec = [] 
        for i in range(1,l): 
            index_skew = modulo_in_range(int(self.prg()),[1,l]) 
            skew_vec.append((i,index_skew)) 
        skew_direction = 1 
        return label,skew_vec,skew_direction