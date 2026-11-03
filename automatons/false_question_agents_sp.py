from falses.bi_dag_function import * 
from falses.hyp_container_gp import * 

class FQSubjectTypeSP: 

    def __init__(self,de_secret:SecretSpaceTypeDAG): 
        assert type(de_secret) == SecretSpaceTypeDAG
        self.de_secret = de_secret
        return 

class FQQuestionerTypeSP: 

    def __init__(self,category_set:set,initial_hs_hyp:defaultdict,prg):  

        assert type(prg) in {MethodType,FunctionType}

        # used for hypotheses on subject's activity 
        self.act_hyp = HypothesisContainerTypeGP(num_paths_per_tail_node=1) 
        self.act_hyp.load_starting_nodes(category_set)

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

    def next_hypothesis_on_action(self,df:DAGTraversalFunctionTypeHSD,hyp:NodePath,\
        dag:DAGraphContainer):
        assert type(df) == DAGTraversalFunctionTypeHSD
        assert type(hyp) == NodePath  
        assert type(dag) == DAGraphContainer

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

        C = dag.children_of_node(hyp)

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