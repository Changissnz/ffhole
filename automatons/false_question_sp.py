from .false_question_agents_sp import * 
from morebs2.numerical_generator import prg_to_LCG_stack
from operator import sub 

"""
False Question Type (S)ecret (P)reservation. 

Consists of two agents, a questioner `Q` and a subject `S` of questioning. 

There are two primary graphs in operation, both directed acyclic graphs (DAG). They are 
an Action Graph G_a that both `Q` and `S` travels on and a secret space G_s such 
that the hidden state T of `S`, used by `S` to travel through the Action Graph, 
is a <NodePath> of G_s. This <NodePath> can also be represent as a map M_t, 
    state (layer) --> label set (nodes of layer). 
Every node n_i of G_a is associated with a boolean activation function F_i. Function 
F_i operates using: 
    - a set of categories C_i from G_s, essentially a DAG; a category is a level 
      of the DAG. 
    - a weight vector W_i, of the same size as the set of categories. 

The two agents travel from root to leaf node of G_a. 
-------------------------------------------------------------------------------------
            **Procedure** 

Suppose that there are r root nodes of G_a. Then `Q` initializes r action hypotheses, 
a path at every node of the r nodes. 

At every timestamp of travel, `Q` queries `S` with every one of its hypotheses. A hypothesis 
question from `Q` consists of: 
- a predicted next node n_c (action) from a reference node n_r (action) on 
  the Action Graph [the hypothesis portion], 
- a question c in the form of a category on the secret [the question portion]. 

`S` will always send a response back, in the form of m <NodePath>s, each one a path of G_s. 
The partitioning of the paths is fixated on question c: 
    PART(m) := <each element a 2-tuple: (label set of c, ratio of the m paths)>. 
NOTE: see description of class<FQSubjectTypeSP> in file<false_question_agents_sp>. 
      In loose terms, if the predicted next node n_c is the node that `S` would have 
      taken if it were at n_r, then the number of paths in PART(m) with the correct 
      label set for category c is dominant. Otherwise, there is an index shift along the 
      ordering of label sets, w.r.t. the ratios of the 1.0 partition. In frequency analysis 
      done by `Q`, the most frequent label set it obtains through registering these responses 
      of m <NodePath>s is its hypothesis on the label set of `c`. The <StateInductionTypeMFUC> 
      is the process that `Q` uses for frequency analysis. In the case where question `c` 
      has already been marked as certain in answer, `Q` chooses that respective label 
      set marked certain instead of the most frequency label set, calculated through 
      the <NodePath>s it receives from `S`. 

The current hypothesis H_h of `Q` on the hidden state of `S` (M_t of T) is the determinant 
on the activation of the node n_r. For any node n_i of G_a, the hidden state hypothesis H_h 
is first mapped to a boolean vector B_i, 
    (C_i,H_h) --> {0,1}*. 
For every category c in C_i, if H_h[c] equals M_t[c], then the boolean for c is 1, otherwise 0. 
Then activation occurs if  
    (B_i * W_i) >= sum(W_i) * t_i; t_i an arbitrary real number in [0.,1.]. 

Boolean outputs of TRUE (activation) forces `S` to send back boolean confirmation: 
    [0] if n_r is the current node that `S` is at,
    [1] if n_r would have been the next node that `S` travels to if it were at. 
NOTE: boolean [0] confirms what nodes of the action hypotheses certainly are the action 
      that `S` took at the beginning of that timestamp. 
      
      Boolean [1] determines if `S`' response of m <NodePath>s back from it certainly 
      yields the most frequent actual label set as the actual label set. If boolean [1] 
      is TRUE, then `Q`'s <StateInductionTypeMFUC> registers c as "certain" in answer, 
      resorting to that most frequent label set from the m <NodePath>s response from 
      that point on. 

------------------------------------------------------------------------------------------
            **Objective** 

The traversal of `S` through Action Graph G_a allows for questioner `Q` to uncover the hidden 
state (full or partial) of `S`. The uncovering of `S`' hidden state is objective #1 for `Q`. 

`Q`'s objective #2 is to correctly identify the actions (nodes) that `S` took in its entire 
traversal of G_a. 

NOTE: in the current code implementation, the hidden state of `S` does not change throughout 
the course of execution. It is a static <NodePath> of an arbitrary DAG. 
""" 
class FalseQuestionTypeSP: 

    def __init__(self,Q:FQQuestionerTypeSP,subject:FQSubjectTypeSP,action_graph:ActionGraphTypeDAGLT,\
        action_graph_op:DAGTraversalFunctionTypeHSD): 

        assert type(Q) == FQQuestionerTypeSP
        assert type(subject) == FQSubjectTypeSP
        assert type(action_graph) == ActionGraphTypeDAGLT
        assert type(action_graph_op) == DAGTraversalFunctionTypeHSD

        self.Q = Q 
        self.subject = subject 
        self.action_graph = action_graph
        self.action_graph_op = action_graph_op

        self.preproc()
        self.fin_stat = False 

        self.Q_max_obj_1 = len(self.obj_1_score(full_output=False)[0]) 
        self.Q_max_obj_1_t_index = 0 
        return 

    def preproc(self): 
        self.subject.first_move(self.action_graph)
        self.Q.act_hyp.load_starting_nodes(deepcopy(self.action_graph.l2n_map[0]))
        return     

    def set_prg(self,prg,is_subject:bool): 
        assert type(prg) in {MethodType,FunctionType} 
        assert type(is_subject) == bool 

        if is_subject: 
            self.subject.prg = prg 
        else: 
            self.Q.prg = prg         

    """
    main method #1
    """
    def __next__(self): 

        if self.fin_stat: return 

        # have `Q` predict the next node that `subject` travels to, for 
        # every one of its hypotheses. 
        self.process_Q_hypotheses() 
        self.Q.increment_timestamp()

        # have `subject` make its action on action graph 
        stat2 = self.subject.next_action(self.action_graph,self.action_graph_op)

        self.update_score_record() 

        self.fin_stat = self.subject.fin_stat and self.Q.fin_stat 
        return  

    def process_Q_hypotheses(self): 

        stat = True 
        self.Q.reset_iter() 

        while stat: 
            q = self.process_one_hyp()

            # finished 
            if type(q) == type(None): 
                stat = False 
            
            if self.Q.fin_stat: stat = False 

        self.Q.check_fin_stat()

        if self.Q.fin_stat: 
            self.Q.act_hyp.flush_queue(clear_first=True) 
        return self.Q.fin_stat 

    def process_one_hyp(self): 

        h,node_res_seq,q,fin_stat  = self.Q.process_next_hyp(self.action_graph_op,self.action_graph)

        # case: finished 
        if fin_stat:
            self.Q.act_hyp.flush_queue(clear_first=True) 
            return None 

        # case: hypothesis reached end of actions 
        if type(h) == type(None): 
            return True 

        # case: all questions have been answered and answers marked for certainty
        ##if type(q) == type(None): 
        ##    self.Q.act_hyp.flush_queue() 
        ##    return None 

        # transmit Q's query to subject 
        q_hs_hyp = self.Q.current_hidden_state_hyp()

        # subject responds to Q's query 
        lfeedback,cfeedback = self.subject.respond_to_Q_hyp(q,self.action_graph,\
            self.action_graph_op,h.tail(),node_res_seq,q_hs_hyp)

        self.Q.recv_feedback(lfeedback,cfeedback)

        p_response = self.subject.paths_for_response() 

        for p in p_response: 
            M = nodepath_to_s2l_map(self.subject.de_secret.dag,p)
            self.Q.recv_probable_secret(M) 
        return self.Q.h_conclusion() 

    #------------------------------------ scoring functions for Subject objectives 

    def update_score_record(self): 
        q = len(self.obj_1_score(full_output=False)[0])
        if q > self.Q_max_obj_1: 
            self.Q_max_obj_1 = q
            self.Q_max_obj_1_t_index = self.Q.act_hyp.t_index 

    """
    return: 
    - full_output = True -> 
        [0] set of categories that Q knows 
        [1] number of categories 
        [2] first,timestamp that Q acquired knowledge on the highest number of categories 
      full_output = False -> 
        [0] set of categories that Q knows 
        [1] number of categories 
    """
    def obj_1_score(self,full_output:bool=False): 
        actual_map = self.subject.de_secret.secret_path_map()
        predicted_map = self.Q.current_hidden_state_hyp()

        matches = set() 
        for k,v in actual_map.items(): 
            if k in predicted_map: 
                if predicted_map[k] == v: 
                    matches |= {k} 
        
        if full_output: 
            return matches,len(actual_map),self.Q_max_obj_1_t_index
        return matches,len(actual_map)

    """
    return:
    - [0] number of node matches over moves,
      [1] total number of moves,
      [2] size of Q's hypothesis on S' action path. 
    """
    def obj_2_score(self): 
        X = self.Q.current_action_sequence_hyp()

        q_hyp_size = 1 
        num_matches = 0 
        for k,v in X.items(): 
            actual = self.subject.tpath[k]
            
            q_hyp_size *= len(v) 

            if actual in v: 
                num_matches += 1 

        return num_matches,len(self.subject.tpath),q_hyp_size

    #--------------------------------------------------------------------- 

    @staticmethod 
    def generate_std_instance(initial_q_hypothesis_correct_ratio,prg): 

        # generate the DAG secret 
        sspace = SecretSpaceTypeDAG.generate_std_instance(prg)

        # generate the action graph 
        s2l_map = sspace.secret_path_map()
        A = ActionGraphTypeDAGLT.generate_std_instance(prg,s2l_map)

        # generate the graph traversal operator for the action graph
        cycle_length = modulo_in_range(int(prg()),[15,30])
        prg_ = prg_to_LCG_stack(prg,2,[add,sub])

        L = [int(prg_()) for _ in range(14)] 
        N = NoiseAddedIterableContainer(L,None)  

        op = DAGTraversalFunctionTypeHSD(sspace.dag,N)

        # generate the subject 
        #       NOTE: subject is assigned a stacked LCG of between 3-8 LCGs 
        #       from `prg`. 
        num_lcgs = modulo_in_range(int(prg()),[3,9])
        prg1 = prg_to_LCG_stack(prg,num_lcgs,[add,sub,sub]) 
        subject = FQSubjectTypeSP(sspace,prg1) 

        # generate the questioner 
        cat_set = set(sspace.dag.l2n_map.keys())

        initial_hs_hyp = generate_s2l_hyp_map(sspace.dag,s2l_map,\
            initial_q_hypothesis_correct_ratio,prg)
        
        #       NOTE: questioner is assigned a stacked LCG of between 4-7 LCGs 
        #       from `prg`. 
        num_lcgs = modulo_in_range(int(prg()),[4,8])
        prg2 = prg_to_LCG_stack(prg,num_lcgs,[add,sub])
        Q = FQQuestionerTypeSP(cat_set,initial_hs_hyp,prg2) 

        return FalseQuestionTypeSP(Q,subject,A,op)