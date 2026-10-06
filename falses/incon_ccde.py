from morebs2.disjoint_kcy import * 
from morebs2.numerical_generator import default_std_Python_prng


def cumulative_modulo_boolean_function(modulo,true_output_set:set):  
    assert is_vector(np.array(V)) 
    q = np.sum(V) % modulo 
    return q in true_output_set

"""
Inconsistent Model Type (C)yclical (C)omponent of (D)emonstration and (E)xecution. 

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

    def __init__(self,cperiod_seq:list,F,F_o,contra_mode:int=-1):  
        self.kcy = DisjointKCyclesIterator(cperiod_seq,hop=1)

        assert contra_mode in {-1,0,1,2}

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

        self.Q = deque() 
        self.contra_seq = deque() 
        return 

    def __next__(self): 
        q = next(self.kcy) 
        return self.F(q)

    def switch_contra(self,ext_prng): 
        self.contra_mode = modulo_in_range(int(ext_prng()),[-1,4]) 

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
        self.contra_seq.clear() 

        for _ in range(num_iter): 
            x = next(self) 
            x_ = self.map_result_by_contra(x,True) 

            self.contra_seq.append(self.contra_mode) 
            self.switch_contra() 
            self.Q.append(x_)  
        return list(self.Q) 

    def exec_iterate(self): 
    
        q = [] 
        while len(self.Q) > 0: 
            x = self.Q.popleft() 
            self.contra_mode = self.contra_seq.popleft() 
            x_ = self.map_result_by_contra(x,False)
            q.append(x_)
        return q 