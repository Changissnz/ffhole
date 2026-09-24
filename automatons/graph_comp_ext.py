from xFS_bots.graph_models.community import graph_component_size
from xFS_bots.graph_models.shortest_paths_approx import average_edge_distance_to_nodeset
from xFS_bots.graph_models.shortest_paths import BDFSCache 

def prg_next_neighbor_from_nodeset(G,nodeset,prg): 
    q = prg_seqsort(nodeset,prg) 

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

    min_paths,_ = BDFSCache.BFS_full(G,nodeset,return_type="distance",prg=prg,max_search_radius=float('inf'),\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,verbose=False)

    nodes = sorted(set(G.keys()) - nodeset) 

    node_to_average_distance = dict() 

    for n in nodes: 
        d = average_edge_distance_to_nodeset(n,nodeset,min_paths,is_weighted=False)
        nodes_to_average_distance[n] = d 

    l = [(n,v) for n,v in nodes_to_average_distance.items()]
    sorted_nodes = prg_seqsort_ties(l,prg,vf=lambda x: x[1])[::-1]
    endpoints = sorted_nodes[:num_endpoints] 
    return [p[0] for p in endpoints]   
