from .dag_secret import * 

"""
Traversal Graph Function Type (H)idden (S)tate (D)irected. 
"""
class TraversalGraphFunctionTypeHSD:

    def __init__(self,current_node_loc,hidden_state_map,node_to_assoc_states_map,F):
        assert type(current_node_loc) == type(None) or current_node_loc in node_to_assoc_states_map
        assert None not in hidden_state_map and None not in node_to_assoc_states_map
        assert type(hidden_state_map) == dict 
        assert type(node_to_assoc_states_map) in {defaultdict,dict} 
        for k,v in node_to_assoc_states_map: 
            assert type(v) == set 
            assert v.issubset(set(hidden_state_map.keys())) 

        assert type(F) in {MethodType,Functiontype}

        self.current_node_loc = current_node_loc
        # effectively acts as the "secret", the blackbox variable by which this 
        # function operates by. 
        #       category -> label 
        self.hs_map = hidden_state_map 
        #       node idn -> set of categories (subset in `hs_map`)
        self.n2as_map = node_to_assoc_states_map
        # 
        self.F = F 
        return 

    def update_node_loc(self,n): 
        assert n in node_to_assoc_states_map 
        self.current_node_loc = n  
        return 

    def next_node(self,current_node,hs_hyp):
        return -1 

    def certainty_of_node_location(self,node_location,hs_hyp): 
        return -1  

    @staticmethod 
    def generate_instance__v2(): 
        return -1 

    @staticmethod 
    def generate_instance():
        return -1 

"""
State Induction Type (M)ost (F)requent (U)nless (C)ertain. 
"""
class StateInductionTypeMFUC: 

    def __init__(self): 
        return -1 
