from collections import defaultdict 
from morebs2.point_sorter import min_or_max_rank_in_sequence
from copy import deepcopy

#DEFAULT_SET_KEY_DECODE_FUNCTION = lambda x: set(string_to_vector(x)) 

"""
State Induction Type (M)ost (F)requent (U)nless (C)ertain. 

A hypothesis structure that can be used in applications such as observation of 
Bi-DAG activity, in order to induce its hidden state. 

NOTE: 
the default `key_decode_function` is intended for vector-like data. 
"""
class StateInductionTypeMFUC: 

    def __init__(self,state_set:set,initial_hs_hyp:defaultdict=defaultdict(set)): 
        assert type(state_set) == set 
        assert type(initial_hs_hyp) == dict  
        assert set(initial_hs_hyp.keys()).issubset(state_set) 

        self.state_set = state_set

        # state -> label set 
        self.current_hyp = initial_hs_hyp

        # state -> labelset -> frequency 
        self.fmap = defaultdict(dict) 

        # state -> ?is certain of current hypothesis on label? 
        self.s2c_map = {c:False for c in state_set}
        return 

    """
    outputs the questions that have not been marked as "certain" 
    in answers (see `s2c_map`). 

    These questions are further divided into those that have not 
    been asked yet (no entry in `fmap`) and those that have been 
    (present entry in `fmap`). 
    """
    def active_questions(self): 
        S = self.state_set - self.certain_states()

        answered = S.intersection(set(self.fmap.keys())) 
        not_answered = S - answered 
        return not_answered,answered 

    def certain_states(self): 
        return {k for k,v in self.s2c_map.items() if v} 

    def uncertain_states(self): 
        return {k for k,v in self.s2c_map.items() if not v} 

    def update_certainty(self,s2c_map): 
        assert type(s2c_map) == dict 
        assert set(s2c_map.keys()).issubset(self.category_set)

        for k,v in s2c_map.items(): 
            assert type(v) == bool 
            self.s2c_map[k] = v 
        return 

    def set_certain_category(self,c,l):
        assert c in self.state_set
        assert type(l) != type(None) 

        self.s2c_map[c] = True 
        self.current_hyp[c] = l  
        return 

    def max_labelset_for_category(self,c): 
        assert c in self.category_set

        if c not in self.fmap: 
            return None 

        d = self.fmap[c] 
        if len(d) == 0: return None 

        l2v = [(k,v) for k,v in d.items()] 

        lset = min_or_max_rank_in_sequence(l2v,vf=lambda x:x[1],is_min_rank=False)
        return set(lset) 

    def add_frequencies_to_category(self,c,f:dict): 
        assert c in self.category_set
        assert type(f) == dict 

        if c not in self.fmap: 
            self.fmap[c] = defaultdict(int) 

        for k,v in f.items(): 
            assert type(v) == int and v >= 0 
            self.fmap[c][k] += v 
        return 

    def update_induction(self): 
        rem_cats = self.category_set - set(self.s2c_map.keys()) 

        for c in rem_cats: 
            q = self.max_label_for_category(c)
            self.current_hyp[c] = q 

        return 

    def state_induction(self): 
        return deepcopy(self.current_hyp)