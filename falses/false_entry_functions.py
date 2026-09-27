from morebs2.ssi_ext import * 
from morebs2.numerical_generator import prg_seqsort
from itertools import permutations
from math import factorial

# TODO: relocate these methods 

def best_solutions_loop(q,score_function,output_function): 

    best = [] 
    best_score = -float('inf') 

    for q_ in q: 

        # TODO: 
        score = score_function(q_)
        if score > best_score: 
            best.clear() 

        if score >= best_score: 
            best.append(output_function(q_)) 
            best = best_score 
    return best,best_score

def boolean_conditional_over_map(d,cf): 
    for k,v in d.items(): 
        if not cf(v): return False 
    return True 

#------------------------------ 

def sequential_trap(G,agent_locations,agent_ordering): 
    assert set(agent_ordering) == set(agent_locations.keys())

    used_nodes = set() 
    agent_traps = [] 
    for a in agent_ordering: 
        a2 = agent_locations[a]
        neighbors = G[a2] 

        if len((neighbors | {a2}).intersection(used_nodes)) == 0: 
            agent_traps.append(a) 
            used_nodes |= neighbors 
    return agent_traps 

"""

""" 
def possible_graph_traps(G,agent_locations,max_candidate_size): 

    # get agent neighbor intersections 
    agent_intersections = [] 
    A = sorted(agent_locations.keys()) 

    P = permutations(A,len(A)) 

    Q = [] 

    i = 0 
    for p in P: 
        t = sequential_trap(G,agent_locations,p) 
        if set(t) not in Q: 
            Q.append(set(t))
            yield t  
        i += 1 
        if i >= max_candidate_size: break 

    return

"""
return: 
- 
"""
def satisfied_trap_config(G,t_nodes,node_to_expected_weight_range_map,node_weight_map,prg):  

    t_nodes = prg_seqsort(sorted(t_nodes),prg) 
    sat_traps = set() 

    for t in t_nodes: 
        q = node_weight_map[t] 
        q_range = node_to_expected_weight_range_map[t] 
        d = 0 
        if q > q_range[1]: 
            d = q_range[1] - q 
        elif q < q_range[0]: 
            d = q_range[0] - q 

        node_weight_map,stat = even_till_zero_distribution(node_weight_map,t,peripheral= deepcopy(G[t]),delta=d) 

        if not stat: 
            return node_weight_map,sat_traps 
        sat_traps |= {t} 

    return node_weight_map,sat_traps

def fetch_satisfied_traps(node_weight_map,node_to_expected_weight_range_map): 
    s = set() 
    for k,r in node_to_expected_weight_range_map.items(): 
        w = node_weight_map[k] 
        if r[0] <= w <= r[1]: 
            s |= {k}
    return s 



## TODO: work on this part. 
def max_traps(G,agent_locations):
    q = possible_graph_traps(G,agent_locations,float('inf')) 
    f = lambda x: len(set(q_))
    return best_solutions_loop(q,f,set) 

def max_traps_with_boolean_conditional(G,agent_locations,node_to_expected_weight_range_map,node_weight_map,prg,max_candidate_size): 

    q = possible_graph_traps(G,agent_locations,max_candidate_size) 

    def f(q_): 
        t_nodes = [agent_locations[q1] for q1 in q_] 
        node_weight_map_,sat_traps = satisfied_trap_config(G,t_nodes,\
            node_to_expected_weight_range_map,deepcopy(node_weight_map),\
            prg)
        return node_weight_map_,sat_traps 

    best = [] 
    best_score = -float('inf')
    for q_ in q: 
        nwm,st = f(q_)
        if len(st) > best_score: 
            best.clear() 

        if len(st) >= best_score and nwm not in best:
            best.append(nwm)
            best_score = len(st) 
    return best,best_score 

"""
return: 
- dict, node -> float delta 
"""
def even_till_zero_distribution(node_weight_map:dict,central_node,peripheral:set,delta):
    if delta == 0: return node_weight_map, True 

    if len(peripheral) == 0: 
        return node_weight_map,False 

    central_weight = node_weight_map[central_node]

    # case: negative for central  
    if delta < 0: 
        x = abs(delta / len(peripheral)) 
        node_weight_map[central_node] += delta 
        for p in peripheral: node_weight_map[p] += x 

        stat = boolean_conditional_over_map(node_weight_map,cf= lambda x: x >= 0)
        return node_weight_map,stat 

    # case: positive for central 
    else: 

        def g(remaining_delta): 
            x = [p for p in peripheral if node_weight_map[p] > 0] 
            if len(x) == 0: 
                return None,None,False 

            even_split = remaining_delta / len(x) 
            return even_split,x,True 

        # every peripheral node gives even support till zero 
        
        while delta > 0: 
            even_split,x,stat = g(delta) 
            if not stat: 
                return node_weight_map,False 

            P = [node_weight_map[p] for p in x] 
            delta_ = min([even_split] + P) 

            for p in x:  
                node_weight_map[p] -= delta_ 

            node_weight_map[central_node] += (delta_ * len(x)) 
            delta -= (delta_ * len(x)) 
        stat = boolean_conditional_over_map(node_weight_map,cf = lambda x: x >= 0)
        return node_weight_map,stat
