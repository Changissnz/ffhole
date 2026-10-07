from morebs2.disjoint_kcy import * 
from morebs2.numerical_generator import default_std_Python_prng,modulo_in_range,\
    safe_modulo_in_range,prg__single_to_int,prg_choose_n
from collections import deque 

DEFAULT_MAX_KCYCLE_FUNCTION_MODULAR_RANGE = [300,331] 
DEFAULT_KCYCLE_CPERIOD_LENGTH_RANGE = [4,202] 
DEFAULT_KCYCLE_SIZE_RANGE = [5,17] 

def cumulative_modulo_boolean_function(modulo,true_output_set:set):

    def f(V):   
        assert is_vector(np.array(V)) 
        q = np.sum(V) % modulo 
        return q in true_output_set

    return f 

def generate_kcycle_function__CMB(cperiod_seq,modulo_ratio_range,output_ratio_range,prg):  
    V = np.array(cperiod_seq) - 1
    s = np.sum(V)
    assert s >= 7, "sum of (sequence - 1) must be at least 7" 
    assert np.min(cperiod_seq) >= 2 

    q = safe_modulo_in_range(prg(),modulo_ratio_range) 
    x = int(round(s * q))

    if x >= DEFAULT_MAX_KCYCLE_FUNCTION_MODULAR_RANGE[1]: 
        x = modulo_in_range(int(prg()),DEFAULT_MAX_KCYCLE_FUNCTION_MODULAR_RANGE) 

    q2 = safe_modulo_in_range(prg(),output_ratio_range) 
    num_qual = int(round(x * q2))

    x2 = [i for i in range(x)] 

    prg_ = prg__single_to_int(prg)     
    qual = set(prg_choose_n(x2,num_qual,prg_,is_unique_picker=True)) 
    return cumulative_modulo_boolean_function(x,qual) 

"""
Inconsistent Function Type (C)yclical (C)omponent of (D)emonstration and (E)xecution. 

Extension of <DisjointKCyclesIterator> with hop=1 for every cycle. 

A dual-output function. The correlation between demonstrative (prior) outputs 
and executive (post) outputs depends on the contradiction mode this structure is 
in. 

To operate this structure for m values, first call 
- demo_iterate(m). 
Then to get actual (executive) values, call 
- exec_iterate(). 
"""
class InconsistentFunctionTypeCCDE: 

    def __init__(self,cperiod_seq:list,F,F_o,contra_mode:int=-1,record_actual:bool=False):  
        self.kcy = DisjointKCyclesIterator(cperiod_seq,hop=1)

        assert contra_mode in {-1,0,1,2}
        assert type(record_actual) == bool

        # literal function 
        self.F = F 
        # opposing function to `F`
        self.F_o = F_o 

        # 
        self.prev_index_map = None 

        # -1 -> d:1 + e:(d) 
        # 0 -> d:0 + e:(d) 
        # 1 -> d:1 + e:(!d)
        # 2 -> d:0 + e:(!d)
        self.contra_mode = contra_mode 
        self.record_actual = record_actual

        # observed demo 
        self.Q = deque() 
        # actual demo 
        self.Q_ = deque() 
        self.contra_seq = deque() 
        return 

    def __next__(self): 
        q = next(self.kcy) 
        return self.F(q)

    def switch_contra(self,ext_prng): 
        self.contra_mode = modulo_in_range(int(ext_prng()),[-1,3]) 

    def map_result_by_contra(self,x,is_demo_output:bool): 

        if is_demo_output: 
            pos_set = {-1,1} 
        else: 
            pos_set = {-1,0} 

        if self.contra_mode in pos_set: 
            return x 
        return self.F_o(x) 

    def demo_iterate(self,num_iter,ext_prng=None): 

        if type(ext_prng) == type(None): 
            ext_prng = default_std_Python_prng(integer_seed=None,output_range=[-10**5.5,10**5.5],rounding_depth=2)

        self.prev_index_map = self.kcy.current_index() 
        
        self.Q.clear() 
        self.Q_.clear() 
        self.contra_seq.clear() 

        for _ in range(num_iter): 
            x = next(self) 

            if self.record_actual:
                self.Q_.append(x) 

            x_ = self.map_result_by_contra(x,True) 
            self.contra_seq.append(self.contra_mode) 
            self.Q.append(x_)  

            self.switch_contra(ext_prng) 
        return np.array(self.Q) 

    def exec_iterate(self): 
    
        q = [] 
        while len(self.Q) > 0: 
            x = self.Q.popleft() 
            self.contra_mode = self.contra_seq.popleft() 
            x_ = self.map_result_by_contra(x,False)
            q.append(x_)
        return np.array(q) 

    @staticmethod 
    def generate_instance(cperiod_seq:list,prg,modulo_ratio_range=[0.2,0.51],output_ratio_range=[0.12,0.2]): 

        F = generate_kcycle_function__CMB(cperiod_seq,modulo_ratio_range,output_ratio_range,prg)
        F_o = lambda x: not bool(x) 
        contra_mode = modulo_in_range(int(prg()),[-1,3]) 
        return InconsistentFunctionTypeCCDE(cperiod_seq,F,F_o,contra_mode=-1)

    @staticmethod
    def generate_instance_v2(k,prg): 
        l = modulo_in_range(int(prg()),DEFAULT_KCYCLE_SIZE_RANGE)
        cperiod_seq = [modulo_in_range(int(prg()),DEFAULT_KCYCLE_CPERIOD_LENGTH_RANGE) for _ in range(l)]  
        return InconsistentFunctionTypeCCDE.generate_instance(cperiod_seq,prg) 