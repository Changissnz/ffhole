from xFS_bots.graph_models.mesh_graph_gen import * 

"""
Label Interpreter Type Class-Expected Effect. 

Represents an ordered set of k labels and their effects as a square 
mesh graph, G_m. Graph G_m is comprised of k * k nodes in a conventional 
square lattice arrangement, that is, every node has degree of 2,3, or 4. 
The most leftward set of k nodes represent the labels themselves. Each of 
the most rightward set of k nodes represents their respective label's 
effect. The shortest path from label node to effect node is called the 
'direct path' (the parallel to the label). In a square mesh graph, these 
direct paths run row-wise.  

Data structure can be used to calculate S-paths, or skew paths, for any 
of the labels of `label_seq`. When given a label l and a sequence I_shift 
consisting of
    (column index, index shift), 
a kernel sequence S_k is calculated first. This kernel sequence is of 
length |`label_seq`|, each j'th element the j'th node of the direct path of 
l, if there is no skew. If there is a skew, the element is the j'th node of 
another label's direct path. 

The S-path is a super-sequence of S_k. For every i'th contiguous subsequence s_q 
added to the S-path, the ending node of s_q is S_k[i]. The prefix of s_q is the 
vertical path traveled, starting from the i'th node of the (i-1)'th previous column's 
direct path. The direct path associated with every column index i, through the course 
of an S-path, is that of the label of S_k[i]. 
"""
class LabelInterpreterTypeCEE: 

    def __init__(self,label_seq):
        assert len(label_seq) > 0 and type(label_seq) == list \
            and len(set(label_seq)) == len(label_seq)  
        self.label_seq = label_seq

        # label-to-parallel map 
        self.l2p_map = None 
        self.G = None 

        self.preproc() 
        return 

    def preproc(self): 
        starting_idn = 0 
        X = Mesh2DGraphGen(starting_idn,len(self.label_seq),len(self.label_seq))
        X.make()

        self.l2p_map = dict() 
        for (i,l) in enumerate(self.label_seq): 
            head_node = X.parallel_heads[i]
            self.l2p_map[l] = NodePath.from_graph(X.parallels[i],False,head_node) 
        self.G = X.G 

    """
    main method #1. 

    calculates an S-path (skew path) for a label, starting from the label's 
    assigned starting node in the graph up through one of the effect nodes.  

    label := element of `label_set`. 
    skew := list, element is 
        [0] column index,
        [1] index shift (positive integer). 
    skew_direction := -1|1, direction of row index shift for skew. 
    """
    def label_to_s_path(self,label,skew,skew_direction): 

        # get the kernel of the skew path. 
        nodeseq = self.label_to_s_nodeset(label,skew,skew_direction,\
            full_output=True)

        current_label = label 
        current_index = self.label_to_index(label)
        L = len(self.label_seq)
        q = [self.l2p_map[label][0]]   

        for i in range(L): 
            prev = q[-1] 

            # case: direct path node equals skew path node 
            if prev != nodeseq[i][0]: 
                adj_label = nodeseq[i][1] 
                adj_index = self.label_to_index(adj_label)
                j = -1 if adj_index < current_index else 1  
                nseq = self.nodeseq_at_column_span(i,(current_index,adj_index + j)) 

                # just to check 
                assert nseq[-1] == nodeseq[i][0] 

                # add suffix of node sequence to path 
                q.extend(nseq[1:]) 

                # update variables 
                current_label = adj_label 
                current_index = adj_index 

            # move to next index 
            if i < L - 1: 
                next_node = self.l2p_map[current_label][i+1] 
                q.append(next_node) 
        return q 

    """
    return:
    - list, sequence of nodes at `column_index` starting @ `index_span`[0] up 
            till `index_span`[1]. 
    NOTE: Reverse-ranges enabled.
    """ 
    def nodeseq_at_column_span(self,column_index,index_span): 
        assert len(index_span) == 2
        assert 0 <= index_span[0] < len(self.label_seq) 
        assert -1 <= index_span[1] <= len(self.label_seq) 

        inc = 1 
        if index_span[0] > index_span[1]: 
            inc = -1 

        q = [] 

        i = index_span[0] 
        while i != index_span[1]: 
            label = self.rindex_to_label(i)
            P = self.l2p_map[label]
            n = P[column_index]
            q.append(n) 
            i += inc 
        return q

    """
    return:
    - list, length of |`label_seq`|, every i'th index corresponds to a 
      node of one of the direct paths for the labels, depending on the 
      index shift specified by `skew`. 
    """
    def label_to_s_nodeset(self,label,skew,skew_direction,full_output:bool=False): 
        base_index = self.label_seq.index(label) 

        assert type(skew) == list 
        L = len(self.label_seq)
        for x in skew: 
            assert 0 <= x[0] < L 
            assert type(x[1]) == int and 0 < x[1] 
        assert skew_direction in {1,-1} 

        q = [] 

        def add_to_q(nodionos,labelle): 
            if full_output: 
                q.append((nodionos,labelle))
            else: 
                q.append(nodionos)
            return 

        current_index = 0
        while current_index < len(self.label_seq): 
            n = None 
            label_ = label  

            try:
                print("\tSKEWSOS: ",skew[0],current_index)
            except:
                pass 

            # case: no more skews, go with default  
            if len(skew) == 0: 
                n = self.label_to_node_at_cindex(label,current_index) 

            # case: skew exists at index 
            elif skew[0][0] == current_index: 
                j = (base_index + skew[0][1] * skew_direction) % len(self.label_seq)
                other_label = self.label_seq[j] 
                label_ = other_label
                n = self.label_to_node_at_cindex(other_label,current_index) 
                skew.pop(0)
            # case: skew does not exist, go with default 
            else: 
                n = self.label_to_node_at_cindex(label,current_index) 

            print("XX: ",n,label_) 
            add_to_q(n,label_) 
            current_index += 1 

        return q 

    """
    return:
    - the node for the label's direct path at the 
      specified column index. 
    """
    def label_to_node_at_cindex(self,label,index): 
        assert label in self.l2p_map
        assert 0 <= index < len(self.label_seq) 

        P = self.l2p_map[label] 
        print("PX: ",P)
        return P[index]

    """
    return: 
    - the index of the label in the ordered set of 
      labels. 
    """ 
    def label_to_index(self,label):
        assert label in self.l2p_map
        return self.label_seq.index(label) 

    """
    return:
    - the label in `label_seq` @ `index`.
    """
    def rindex_to_label(self,index): 
        assert 0 <= index < len(self.label_seq)
        return self.label_seq[index]

    """
    return:
    - the label of the direct path containing node `n` @ `index`. 
    """
    def label_of_node_at_index(self,n,index):  
        assert 0 <= index < len(self.label_seq) 

        for k,p in self.l2p_map.items(): 
            if p[index] == n: 
                return k 
        return None 