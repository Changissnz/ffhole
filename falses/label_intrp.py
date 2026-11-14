from xFS_bots.graph_models.

"""
Label Interpreter Type Class-Expected Effect. 
"""
class LabelInterpreterTypeCEE: 

    def __init__(self,label_seq):
        assert len(label_seq) > 0 and type(label_set) == list \
            and len(set(label_set)) == len(label_set)  
        self.label_set = label_set

        # label-to-parallel map 
        self.l2p_map = None 
        self.G = None 

        self.preproc() 
        return 

    def preproc(self): 
        starting_idn = 0 
        X = Mesh2DGraphGen(starting_idn,len(self.label_set),len(self.label_set))
        X.make()

        self.l2p_map = dict() 
        for (i,l) in enumerate(self.label_set): 
            self.l2p_map[l] = X.parallels[i] 
        self.G = X.G 

    """
    calculates a path for a label, starting from the label's assigned 
    starting node in the graph up through one of the effect nodes.  

    label := element of `label_set`. 
    skew := list, element is 
        [0] index,
        [1] column index.
    skew_direction := -1|1, direction of row index shift for skew. 
    is_pre_skew := bool, if True then the i'th node of the label's direct path, 
        the parallel of the label, is touched first before traversing other nodes
        of column i. 
    """
    def label_to_path(self,label,skew,skew_direction,is_pre_skew:bool): 
        assert label in self.l2p_map
        assert type(skew) == list 
        assert skew_direction in {1,-1} 
        return 

    def skew_at_index(self,skew_direction): 

        return -1 