from xFS_bots.graph_models.community import graph_component_size
from xFS_bots.graph_models.shortest_paths_approx import average_edge_distance_to_nodeset
from xFS_bots.graph_models.shortest_paths import BDFSCache,DEFAULT_EDGE_COST_FUNCTION_2
from types import MethodType,FunctionType
from morebs2.numerical_generator import prg_seqsort,prg_seqsort_ties,safe_modulo_in_range,is_vector,prg_decimal 
from morebs2.measures import vec_to_frequency_map
from morebs2.matrix_methods import is_valid_range
import numpy as np 

def prg_next_neighbor_from_nodeset(G,nodeset,prg): 
    q = prg_seqsort(sorted(nodeset),prg) 

    for n in q: 
        neighbors = G[n] 
        x = sorted(nodeset - neighbors)

        if len(x) == 0: continue 
        
        return x[int(prg()) % len(x)] 
    return None 

"""
G := defaultdict, connected component 
"""
def prg_choose_connected_component(G,component_size,prg): 
    assert graph_component_size(G) == 1 
    assert len(G) >= component_size 

    V = sorted(G.keys()) 

    start = int(prg()) % len(V) 

    q = set([V.pop(start)]) 

    for _ in range(component_size - 1):
        q2 = prg_next_neighbor_from_nodeset(G,q,prg)
        assert type(q2) != type(None) 
        q |= {q2} 
    return q

def prg_choose_farthest_endpoints_from_nodeset(G,nodeset,num_endpoints,prg):

    min_paths,_ = BDFSCache.BFS_full(G,nodeset,return_type="paths",prg=prg,max_search_radius=float('inf'),\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,verbose=False)

    nodes = sorted(set(G.keys()) - nodeset) 

    node_to_average_distance = dict() 

    for n in nodes: 
        d = average_edge_distance_to_nodeset(n,nodeset,min_paths,is_weighted=False)
        node_to_average_distance[n] = d 

    l = [(n,v) for n,v in node_to_average_distance.items()]
    sorted_nodes = prg_seqsort_ties(l,prg,vf=lambda x: x[1])[::-1]
    endpoints = sorted_nodes[:num_endpoints] 
    return [p[0] for p in endpoints]   

#------------------------------------

def frequency_of_range_for_vector(V,r): 
    V = np.array(V) 
    assert is_vector(V) 
    assert is_valid_range(r,True,True) or is_valid_range(r,False,True)

    return len([v for v in V if r[0] <= v <= r[1]]) 

# TODO: look for duplicate code 
def prg_choose_subrange_for_n_elements(numbers,n,prg,starting_index = None,\
    default_zero_distance=5.0,default_zero_diameter=1.0):

    assert type(numbers) in {np.ndarray,list} 
    assert 0 <= n <= len(numbers)

    minumum,maximum = min(numbers),max(numbers)

    # case: no elements 
    if n == 0: 
        if prg_decimal(prg,[0.,1.]) <= 0.5: 
            q = minumum - default_zero_distance
            q0 = q - default_zero_diameter 
            return [q0,q] 
        else: 
            q = maximum + default_zero_diameter
            q0 = q + default_zero_diameter 
            return [q,q0] 

    # case: all elements 
    if n == len(numbers): 
        return [minumum,maximum]

    start = None 
    n_ = 0 
    occupied = set() 
    vf = vec_to_frequency_map(np.array(numbers))

    # case: starting index is given  
    if type(starting_index) != type(None): 
        assert 0 <= starting_index < len(numbers) 
        assert type(starting_index) in {int,np.int32,np.int64} 
        start = numbers[starting_index]
        numbers = sorted(set(numbers)) 
        starting_index = list(numbers).index(start) 
    # case: starting index not given 
    else:
        numbers = sorted(set(numbers)) 

        # choose a least frequent element 
        F = [(k,v) for k,v in vf.items()]
        F = prg_seqsort_ties(F,prg,vf=lambda x: x[1])
        start = F[0][0] 
        starting_index = numbers.index(start) 
    
    n_ += vf[start] 
    span = [start,start]

    left_index,right_index = starting_index - 1, starting_index + 1 

    while n_ < n: 
        left_delta,right_delta = None,None 
        X = []

        if left_index >= 0:  
            q0 = numbers[left_index] 
            left_delta = n_ + vf[q0] 
            X.append(("0",abs(n-left_delta))) 

        X.append(("-1",abs(n-n_)))

        if right_index < len(numbers): 
            q0 = numbers[right_index] 
            right_delta = n_ + vf[q0] 
            X.append(("1",abs(n-right_delta))) 

        X = prg_seqsort_ties(X,prg,lambda x:x[1])
        q = X[0] 
        if q[0] == "0": 
            span[0] = numbers[left_index] 
            occupied |= {numbers[left_index]}
            left_index -= 1 
            n_ = left_delta 
        elif q[0] == "-1": 
            break 
        else: 
            span[1] = numbers[right_index]
            occupied |= {numbers[right_index]}
            right_index += 1 
            n_ = right_delta
    return span 