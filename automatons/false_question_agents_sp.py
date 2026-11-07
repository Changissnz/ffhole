from falses.bi_dag_function import * 
from falses.hyp_container_gp import * 
from morebs2.numerical_generator import prg_partition_for_float

class FQSubjectTypeSP: 

    def __init__(self,de_secret:SecretSpaceTypeDAG,prg): 
        assert type(de_secret) == SecretSpaceTypeDAG
        assert type(prg) in {MethodType,FunctionType}
        self.de_secret = de_secret
        self.prg = prg 

        self.loc = None 
        return 

    """
    first move on arbitrary Action Graph is assigned 
    by `prg`. All moves after first move depend on 
    hidden state, `de_secret`. 
    """
    def first_move(self,G): 
        assert issubclass(type(G),DAGraphContainer) 

        q = sorted(G.l2n_map[0]) 
        assert len(q) > 0 

        i = int(self.prg()) % len(q)
        
        self.loc = q[i]
        return q[i] 

    """
    q_nr_vec := list, each element is 
        [0] next node from current node 
        [1] ratio of paths that include a specific label (node) of 
            a category (the `question`). 

    return:
    - 
    """
    def respond_to_Q_hyp(self,question,agraph:ActionGraphTypeDAGLT,action_graph_op:DAGTraversalFunctionTypeHSD,\
        current_node,q_predicted_node,q_nr_vec): 

        assert type(agraph) == ActionGraphTypeDAGLT
        assert question in agraph.G 
                
        actual_next = self.next_node_from_current_node(agraph,action_graph_op,current_node) 
        C = agraph.children_of_node(current_node,True)
        a2l_vec = self.a_node_to_lset_vec(actual_next,C,question,q_nr_vec)

        return 

    #------------------------------------------- used for action graph traversal 

    """
    calculates the next node on `agraph` (Action Graph), starting from `current_node` 
    using the traversal operator `action_graph_op`. 
    """
    def next_node_from_current_node(self,agraph:ActionGraphTypeDAGLT,\
        action_graph_op:DAGTraversalFunctionTypeHSD,current_node): 

        assert type(agraph) == ActionGraphTypeDAGLT
        assert type(action_graph_op) == DAGTraversalFunctionTypeHSD

        hidden_state_map = self.de_secret.secret_path_map()
        return action_graph_op.next_from_node(hidden_state_map,agraph,current_node) 

    #------------------------------------------- used for assigning ratios of secret paths

    """
    next action nodeset to secret state labelset vector. 
    Output used to calculate the secret's paths to be sent to the questioner, based 
    on ratios of the paths containing the assigned answer (label set) to the question.  

    calculates a vector w/ every element of the following: 
    [0] next action node
    [1] label-set for `question` corresponding to this next action node 
    [2] r in [0.,1.], ratio of paths containing label-set from [1] 
    """
    def a_node_to_lset_vec(self,actual_anode,question,q_nr_vec): 
        assert actual_anode in next_anodeset

        # NOTE: inefficient call (calculates entire state-to-labelset map)
        s2l_map = self.de_secret.secret_path_map()
        s2l_map = {question:s2l_map[question]} 

        # case: only one next 
        if len(q_nr_vec) == 1: 
            return [(actual_anode,s2l_map[question],1.0)]

        lx = alternative_label_sort(self.de_secret.dag,s2l_map,question,prg)
        lx_ = [lx1 - s2l_map[question] for lx1 in lx] 

        # case: no available labels after removing the actual labelset
        c = sum([len(l) for l in lx_]) 
        if c == 0: 
            lx_ = lx 
        
        # removing empty sets 
        lx_ = [l for l in lx_ if len(l)] 
        lx_ = lx_[::-1] 

        # make the sequence of labels, with the first one being 
        # actual label 
        label_sets = [s2l_map[question]] 
        for i in range(len(q_nr_vec) - 1): 
            j = i % len(lx_) 
            label = lx_[j] 
            label_sets.append(label) 

        # get the index of actual action from `q_nr_vec`
        q_predicted_node_order = [nr[0] for nr in q_nr_vec]
        i = q_predicted_node_order.index(actual_anode)

        # shift `label_sets` by `i` indices to the right. 
        label_sets = subvec(label_sets,i,len(label_sets)) 

        # merge `q_nr_vec` with `label_sets`
        q_nr_vec2 = [] 
        for l,nr in zip(label_sets,q_nr_vec): 
            q_nr_vec2.append((nr[0],l,nr[1])) 
        return q_nr_vec2

    #----------------------------------------------- used for determining if questioner's 
    #----------------------------------------------- current hypothesis on hidden state of 
    #----------------------------------------------- subject activates the location feedback 
    #----------------------------------------------- 

    def location_feedback(self,agraph:ActionGraphTypeDAGLT,q_hs_hyp,node):
        return agraph.boolean_output(node,q_hs_hyp)

class FQQuestionerTypeSP: 

    def __init__(self,category_set:set,initial_hs_hyp:defaultdict,prg):  

        assert type(prg) in {MethodType,FunctionType}

        # used for hypotheses on subject's activity 
        self.act_hyp = HypothesisContainerTypeGP(num_paths_per_tail_node=1) 
        self.act_hyp.load_starting_nodes(category_set)

            # used to iterate through list of hypotheses         
        self.hyp_index = 0 
        self.fin_iter_stat = False 

        # used for Hidden State hypotheses
        self.hs_hyp_mach = StateInductionTypeMFUC(category_set,initial_hs_hyp)
        self.prg = prg   

        self.active_questions = set() 
        return 

    def update_hs_hyp(self): 
        return -1 

    def de_la_question(self,df:DAGTraversalFunctionTypeHSD,hyp:NodePath,dag:DAGraphContainer): 
        node_res_seq = self.next_hypothesis_and_resdist_on_action(df,hyp,dag)
        return -1 

    def uncertain_subject_hidden_states(self): 
        return -1 

    #------------------------------------ used for calculating next hypotheses on action 

    def next_hyp(self): 
        if self.fin_iter_stat: 
            return None 

        if self.hyp_index >= len(self.act_hyp): 
            self.fin_iter_stat = True 
            return None 

        return self.act_hyp[self.hyp_index] 
        

    def next_hypothesis_on_action(self,df:DAGTraversalFunctionTypeHSD,hyp:NodePath,\
        dag:DAGraphContainer):
        assert type(df) == DAGTraversalFunctionTypeHSD
        assert type(hyp) == NodePath  
        assert issubclass(type(dag),DAGraphContainer)

        M = self.hs_hyp_mach.state_induction()
        n = hyp.tail() 
        
        return df.next_from_node(M,dag,n) 
    
    """
    predicts the next node for `hyp`, w.r.t. subject's activity, and assigns resource 
    distribution ratios to all children nodes of the tail node of `hyp`. Resource is 
    used to confirm subject location. 

    return: 
    - list, element is 
        [0] predicted next node 
        [1] ratio of resources distributed to confirm location. 

    NOTE: the first element in the output list is the most prioritized prediction, the one 
        allocated the most resources.  
    """
    def next_hypothesis_and_resdist_on_action(self,df:DAGTraversalFunctionTypeHSD,hyp:NodePath,\
        dag:DAGraphContainer):

        predicted_next = self.next_hypothesis_on_action(df,hyp,dag) 
        if type(predicted_next) == type(None): 
            return None 

        C = dag.children_of_node(hyp.tail())

        if len(C) < 2: 
            return [(predicted_next,1.0)]

        df = len(C) - 1 
        px = prg__single_to_int(self.prg)
        var = 0.5 
        n = 100 
        prt = prg_partition_for_float(0.49,df,px,var,n,rounding_depth=5)

        C_ = sorted(C - {predicted_next}) 
        S = [(predicted_next,0.51)]

        for p,c in zip(prt,C_): 
            S.append((c,p))

        return S 