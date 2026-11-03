from xFS_bots.graph_models.node_path import * 

"""
Hypothesis Container Type (G)raph (P)aths.

Container holds sequence of graph paths `gpaths`, and 
these paths are the hypotheses for an arbitrary object's 
traversal through an arbitrary graph. 

Container is designed to store hypotheses of arbitrary 
object while it is traversing through a graph. 

The `num_paths_per_tail_node` threshold is the maximum 
number of paths with any tail node `n_t` of path. It is 
to limit the number of conflicting candidates for graph 
nodes that currently end at that specific node `n_t`. 
"""
class HypothesisContainerTypeGP:

    def __init__(self,gpaths=None,num_paths_per_tail_node=float('inf')): 
        if type(gpaths) == type(None): 
            gpaths = [] 
        for x in gpaths: assert type(x) == NodePath 
        assert num_paths_per_tail_node >= 1 

        self.gpaths = gpaths 
        self.paths_per_tail = num_paths_per_tail_node

        self.tail2paths = dict() 
        return 

    def load_starting_nodes(self,nodes:set): 

        nodes = sorted(nodes) 
        for n in nodes: 
            P = NodePath(n) 
            self.tail2paths[n] = P 
            self.gpaths.append(P) 
        return 

    def delete_path(self,P,t2p_index=None,p2s_index=None): 
        assert type(P) == NodePath
        if type(t2p_index) == type(None): 
            t2p_index = self.path_to_t2p_index(P) 
            assert t2p_index != -1 
        else: 
            assert P.tail() in self.tail2paths 
            assert self.tail2paths[P.tail()] == t2p_index
        
        self.tail2paths[P.tail()].pop(t2p_index)

        if type(t2p_index) == type(None): 
            p2s_index = self.path_to_seq_index(P) 
            assert p2s_index != -1 
        else: 
            assert P == self.gpaths[p2s_index] 
        self.gpaths.pop(p2s_index)
        return

    def path_to_t2p_index(self,P): 
        assert type(P) == NodePath 
        t = P.tail()
        assert t in self.tail2paths

        for (i,p) in enumerate(self.tail2paths[t]): 
            if p == P: 
                return i 
        return -1 

    def path_to_seq_index(self,P): 
        for (i,p) in enumerate(self.gpaths): 
            if p == P: return i 
        return -1 

    """
    updates path by adding `next_node` to tail, as well as  
    associated weight `next_weight`. Typically, `next_weight` 
    falls in range [0.,1.] and signifies the certainty that 
    object is currently on `next_node`. 
    """ 
    def update_path(self,P,next_node,next_weight):  
        assert type(P) == NodePath 
        P.append(next_node,next_weight)
        return 

    def add_path_to_mem(self,P): 

        stat = self.add_path_to_t2p_map(P) 

        if not stat: return False 

        stat = False 
        for (i,p) in enumerate(self.gpaths): 
            if P.cost() <= p.cost(): 
                self.gpaths.insert(i,P)
                stat = True 
                break 
        
        if not stat: 
            self.gpaths.append(P)
        return True 

    """
    return:
    - ?is path `P` added? 
    """
    def add_path_to_t2p_map(self,P): 
        t = P.tail()

        if t not in self.tail2paths: 
            self.tail2paths[t] = [P] 
            return True 

        index = None 
        for (i,p) in enumerate(self.tail2paths[t]): 
            if P.cost() <= p.cost(): 
                self.tail2paths[t].insert(i,P)
                index = i 
                break 

        if type(index) == type(None): 
            self.tail2paths[t].append(P) 
            index = len(self.tail2paths[t]) - 1 

        while len(self.tail2paths[t]) > self.paths_per_tail: 
            self.tail2paths[t].pop(-1) 

        return index < self.paths_per_tail