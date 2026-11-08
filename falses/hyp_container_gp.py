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

NOTE: the data structure keeps track of relevant nodesets 
      from new or updated paths stored into it. If a path 
      stored into it has tail node marked with weight 1, 
      that tail node is relevant. 0-weights are used to 
      signify uncertainty or incorrectness. 
"""
class HypothesisContainerTypeGP:

    def __init__(self,num_paths_per_tail_node=float('inf')): 
        assert num_paths_per_tail_node >= 1 

        self.gpaths = []  
        # contains deltas from <NodePath>s in `gpaths`
        self.gpaths_queue = [] 
        self.paths_per_tail = num_paths_per_tail_node

        # node idn -> list of paths 
        self.tail2paths = dict() 
        
        # timestamp -> nodeset, used to keep track of marked nodes per timestamp 
        self.tstamp2nodeset = defaultdict(set)
        self.t_index = 0 
        return 

    def display_paths(self,display_mode:int=0):
        assert display_mode in {0,1,2}

        def f(p): 
            if display_mode == 0: 
                print("* ",len(p)) 
                return 
            if display_mode == 1: 
                print("* ",p.p) 
                return     
            print("* ",p)

        for x in self.gpaths: 
            f(x) 

    def __getitem__(self,i):
        if isinstance(i, slice): 
            return self.gpaths.__getitem__(i)    

        if type(i) in {list,np.ndarray}:
            qx = []
            for i_ in i:
                qx.append(self.__getitem__(i_))
            return qx 

        assert i < len(self) 
        return self.gpaths[i]  

    def __len__(self): 
        return len(self.gpaths) 

    def load_starting_nodes(self,nodes:set): 

        nodes = sorted(nodes) 
        for n in nodes: 
            P = NodePath(n) 
            self.tail2paths[n] = [P]
            self.gpaths.append(P) 
        return 

    def delete_path(self,P,t2p_index=None,p2s_index=None): 
        assert type(P) == NodePath
        if type(t2p_index) == type(None): 
            t2p_index = self.path_to_t2p_index(P) 
            #assert t2p_index != -1 
        else: 
            assert P.tail() in self.tail2paths 
            assert self.tail2paths[P.tail()][t2p_index] == P 
        
        if t2p_index != -1: 
            self.tail2paths[P.tail()].pop(t2p_index)
            if len(self.tail2paths[P.tail()]) == 0: 
                del self.tail2paths[P.tail()]

        if type(p2s_index) == type(None): 
            p2s_index = self.path_to_seq_index(P) 
            assert p2s_index != -1 
        else: 
            assert P == self.gpaths[p2s_index] 
        self.gpaths.pop(p2s_index)
        return

    def path_to_t2p_index(self,P): 
        assert type(P) == NodePath 
        t = P.tail()
        if t not in self.tail2paths: return -1 

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
        return P 

    def add_path_to_mem(self,P): 

        stat = self.add_path_to_t2p_map(P) 

        # case: path is not added because tail limit 
        #       reached 
        if not stat: return False 

        # add path to sequence of paths
        stat = False 
        for (i,p) in enumerate(self.gpaths_queue): 
            if P.cost() >= p.cost(): 
                self.gpaths_queue.insert(i,P)
                stat = True 
                break 
        
        if not stat: 
            self.gpaths_queue.append(P)

        # add tail node of P if its weight=1 marks it 
        # as relevant 
        if P.pweights[-1] == 1: 
            self.tstamp2nodeset[self.t_index] |= {P.tail()} 
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
            if P.cost() >= p.cost(): 
                self.tail2paths[t].insert(i,P)
                index = i 
                break 

        if type(index) == type(None): 
            self.tail2paths[t].append(P) 
            index = len(self.tail2paths[t]) - 1 

        self.reduce_tails(t) 
        return index < self.paths_per_tail

    def reduce_tails(self,t): 
        l = len(self.tail2paths[t])
        while len(self.tail2paths[t]) > self.paths_per_tail: 
            P = self.tail2paths[t][l-1]
            self.delete_path(P,l-1,None)
            l = len(self.tail2paths[t])

    def flush_queue(self):
        while len(self.gpaths_queue): 
            p = self.gpaths_queue.pop(0)
            t = p.tail() 
            
            # case: path was not added because of tail limit 
            if p not in self.tail2paths[t]: 
                continue 
            self.gpaths.append(p) 
        return 

    def increment_timestamp(self): 
        self.t_index += 1 