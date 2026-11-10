from falses.bi_dag_function import * 
from falses.state_induction import * 
from falses.hyp_container_gp import * 
from morebs2.numerical_generator import prg_partition_for_float
from morebs2.matrix_methods import subvec 

DEFAULT_SUBJECT_TOTAL_PATHS_PER_RESPONSE = 100 

"""
(F)alse (Q)uestion Subject Type (S)ecret (P)reservation. 

Subject contains a secret, `de_secret`, that acts as a hidden state. 
Subject traverses an Action Graph during the running of the 
False Question Type SP program. Subject uses the hidden state, 
`de_secret`, to decide the path of traversal, node by node from root 
to leaf node. 

The `de_secret` is an instance of class<SecretSpaceTypeDAG>, comprised 
of a directed acyclic graph (DAG), each layer of the graph acting as a category, 
and a path through the DAG. The path's nodes correspond to category label 
sets. 

At every node during traversal, besides from the first, subject is to 
respond to every hypothesis question posed by a questioner of 
class<FQQuestionerTypeSP>, each hypothesis question comprising of the 
following: 
- a predicted next node n_c (action) from a reference node n_r (action) on 
  the Action Graph [the hypothesis portion], 
- a question c in the form of a category on the secret [the question portion]. 

If the reference node n_r is activated on the Action Graph, due to questioner's 
current hypothesis on the hidden state of subject resulting in n_r's linear 
combination expression outputting TRUE, then the following information is 
sent back: 
- boolean confirmation of if n_r is the current node that subject is on, 
- boolean confirmation of if n_c would be the node that subject travels on if 
  it were located on n_r. 
NOTE: the subject's traversal function is designed to be deterministic for every 
      node of the Action Graph. That is, at any instance, subject would travel 
      to n_r' from n_r if it were on n_r. 
NOTE: see description of node activation function in class<ActionGraphTypeDAGLT> 
      of file<bi_dag_function>. 

Additionally, subject sends back a total of `num_paths_per_response`, as an 
answer to question c. These paths of the DAG for `de_secret` fixate on layer c. 
The partitioning of the paths is calculated by method<a_node_vec_to_lset_vec>, 
and is a j-index shift of the questioner's demand of paths, a vector with element 
    (next node from n_r,ratio of paths). 
The node n_c is the top priority (0-index) in this vector. If n_c is the actual 
node that subject would travel on if it were at n_r, then the index shift is 0, 
meaning that the proportion of paths containing the actual label set of category 
c is either 51% or 100% (if there is only one node that can be traveled to from 
n_r). 
NOTE: The proportion of this guarantees that the questioner, with null statistics 
      before this questioning, would obtain statistics that place the actual label 
      set of c as the most frequent. So the questioner would correctly assume what 
      c is. 
If n_c is not the actual node, then there is an index shift on the label set vector 
that subject calculates, usually placing the actual label set as the less frequent 
one. 
"""
class FQSubjectTypeSP: 

    def __init__(self,de_secret:SecretSpaceTypeDAG,prg,\
        num_paths_per_response:int=DEFAULT_SUBJECT_TOTAL_PATHS_PER_RESPONSE): 

        assert type(de_secret) == SecretSpaceTypeDAG
        assert type(prg) in {MethodType,FunctionType}
        assert num_paths_per_response > 0 

        self.de_secret = de_secret
        self.prg = prg 
        self.num_paths_per_response = num_paths_per_response

        self.loc = None
        self.current_l2r_path_demand = None  

        self.fin_stat = False 

        # sequence of nodes subject travels over 
        self.tpath = [] 
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
        self.tpath.append(q[i])
        return q[i] 

    """
    question := int, identifier of question from questioner, 
    q_nr_vec := list, each element is 
        [0] next node from current node 
        [1] ratio of paths that include a specific label (node) of 
            a category (the `question`). 
        * the first element is the top prediction of subject on the 
          next node starting from current node. 
    q_hs_hyp := dict, state -> labelset, questioner's hypothesis on 
            subject's hidden state. 

    return:
    - bool|None, predicted next location from `current_node` is subject's current location. 
    - bool|None, predicted next location from `current_node` is correct choice if subject were 
        move from `current_node`. 
    """
    def respond_to_Q_hyp(self,question,agraph:ActionGraphTypeDAGLT,action_graph_op:DAGTraversalFunctionTypeHSD,\
        current_node,q_nr_vec,q_hs_hyp):  

        assert type(agraph) == ActionGraphTypeDAGLT
        #assert question in agraph.G.l2n_map, "got {}".format(question) 
                
        actual_next = self.next_node_from_current_node(agraph,action_graph_op,current_node) 
        self.current_l2r_path_demand = self.a_node_vec_to_lset_vec(actual_next,question,q_nr_vec)

        lfeedback = self.location_feedback(agraph,q_hs_hyp,current_node)

        # case: feedback enabled, subject responds back with status on if 
        #       its current location matches with questioner's predicted next node. 
        if lfeedback: 
            return self.loc == actual_next,actual_next == q_nr_vec[0][0] 
        return None,None 

    def paths_for_response(self): 
        assert type(self.current_l2r_path_demand) != type(None) 

        pvec = self.num_paths_info() 

        while len(pvec) > 0: 
            # choose a label-set 
            i = int(self.prg()) % len(pvec) 
            lset,total_num = pvec[i] 

            # case: no more of that specific label set 
            if total_num == 0: 
                pvec.pop(i) 
                continue 

            num_selected = modulo_in_range(int(self.prg()),[1,total_num+1]) 
            P = self.de_secret.n_paths_with_nodeset(lset,num_selected,prg=self.prg)

            for p in P: 
                yield p 
            total_num -= num_selected
            pvec[i] = [lset,total_num] 
        return 

    """
    calculates the number of paths per label-set of `current_l2r_path_demand`, 
    using PRNG distribution of remainder at the end.  
    """
    def num_paths_info(self): 
        num_paths_vec = [] 
        c = 0 
        for lset,ratio in self.current_l2r_path_demand:
            num = floor(ratio * self.num_paths_per_response)
            num_paths_vec.append([lset,num])
            c += num 

        diff = self.num_paths_per_response - c 

        if diff > 0: 
            rem_vec = [1] * diff 
            x = prg_safe_uniform_partition_sequence(rem_vec,len(num_paths_vec),\
                self.prg,distribute_remainder_evenly=True) 

            for (i,x_) in enumerate(x): 
                num_paths_vec[i][1] = num_paths_vec[i][1] + sum(x_) 
        return num_paths_vec 

    #------------------------------------------- used for action graph traversal 

    def next_action(self,agraph:ActionGraphTypeDAGLT,\
        action_graph_op:DAGTraversalFunctionTypeHSD): 

        if self.fin_stat: return self.fin_stat 

        next_node = self.next_node_from_current_node(agraph,action_graph_op,self.loc)

        if type(next_node) == type(None): 
            self.fin_stat = True 
            return self.fin_stat 

        self.loc = next_node 
        self.tpath.append(next_node) 
        return self.fin_stat 

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
    maps a next action nodeset to secret state labelset vector. 
    Output used to calculate the secret's paths to be sent to the questioner, based 
    on ratios of the paths containing the assigned answer (label set) to the question.  

    calculates a vector w/ every element of the following: 
    [0] label-set for `question` corresponding to this next action node 
    [1] r in [0.,1.], ratio of paths containing label-set from [1] 
    """
    def a_node_vec_to_lset_vec(self,actual_anode,question,q_nr_vec): 

        # case: no more questions from questioner -> 
        #       subject sends over paths on a question selected 
        #       by its PRNG. 
        if type(question) == type(None): 
            possible_questions = sorted(self.de_secret.dag.l2n_map.keys())
            i = int(self.prg()) % len(possible_questions)
            question = possible_questions[i]

        # NOTE: inefficient call (calculates entire state-to-labelset map)
        s2l_map = self.de_secret.secret_path_map()
        s2l_map = {question:s2l_map[question]} 

        # case: only one next 
        if len(q_nr_vec) == 1: 
            return [(s2l_map[question],1.0)]

        lx = alternative_label_sort(self.de_secret.dag,s2l_map,question,self.prg)
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
            q_nr_vec2.append((l,nr[1])) 
        return q_nr_vec2

    #----------------------------------------------- used for determining if questioner's 
    #----------------------------------------------- current hypothesis on hidden state of 
    #----------------------------------------------- subject activates the location feedback 
    #----------------------------------------------- 

    def location_feedback(self,agraph:ActionGraphTypeDAGLT,q_hs_hyp,node):
        return agraph.boolean_output(node,q_hs_hyp)

"""
(F)alse (Q)uestion Subject Type (S)ecret (P)reservation. 

Questioner objective is of two parts: 
- uncovering the hidden state of subject (possibilities make up a directed acyclic graph) 
    [done through <StateInductionTypeMFUC>]. 
- determining the actions that subject took (traversal through a directed acyclic graph), 
    throughout the course of interaction [done through <HypothesisContainerTypeGP>]. 
"""
class FQQuestionerTypeSP: 

    def __init__(self,category_set:set,initial_hs_hyp:defaultdict,prg):  

        assert type(prg) in {MethodType,FunctionType}

        # used for hypotheses on subject's activity 
        self.act_hyp = HypothesisContainerTypeGP(num_paths_per_tail_node=1) 

            # used to iterate through list of hypotheses         
        self.hyp_index = 0 
        self.fin_iter_stat = False 

        # used for Hidden State hypotheses
        self.hs_hyp_mach = StateInductionTypeMFUC(category_set,initial_hs_hyp)
        self.prg = prg   

        # variables used to store contextual information for every 
        # hypothesis-based question 
            # the hypothesis being worked on by agent 
        self.hyp_in_queue = None 
            # the predicted next node (action) from `hyp_in_queue`
        self.p_next_node = None 
            # status of whether predicted next node is the correct actual location. 
        self.lfeedback = None  
            # status of whether predicted next node is the correct location 
            # if in the event 
        self.cfeedback = None 
            # current question identifier being asked 
        self.q_idn = None 
            # used to store the response of probable secret paths from asking 
            # on hypothesis 
            # state -> label -> count 
        self.tmp_s2l2c_map = dict() 
            # tail node idn -> 
            #   [0] confirmation on location
            #   [1] confirmation on paths on hidden state category
            # *** every hypothesis is associated with a unique tail node 
        self.tail2fb_map = dict() 

        self.fin_stat = False 
        self.num_hyp_deltas = 0 
        return 

    def increment_timestamp(self): 
        self.act_hyp.increment_timestamp()

    def current_hidden_state_hyp(self): 
        return self.hs_hyp_mach.state_induction()

    def current_action_sequence_hyp(self): 
        return self.act_hyp.path_hypothesis() 

    """
    method called after all hypotheses have been updated 
    """
    def check_fin_stat(self): 
        if self.num_hyp_deltas == 0: 
            self.fin_stat = True 

    #------------------------------------ used for calculating next hypotheses on action 

    """
    - return:
    [0] NodePath, hypothesis being acted on,
    [1] list, element is 
            [0] predicted next node 
            [1] ratio of resources distributed to confirm location. 
    [2] question to ask (category of subject' hidden state)
    [3] bool, ?finished with iteration? 
    """
    def process_next_hyp(self,df:DAGTraversalFunctionTypeHSD,\
        dag:DAGraphContainer):

        if self.fin_stat: 
            return None,None,None,True 

        # case: no more hypotheses (unused) 
        if len(self.act_hyp) == 0: 
            return None,None,None,True 

        # choose next hypothesis from memory, and predict the next 
        # action (node) from it. 
        h = self.next_hyp()
        if type(h) == type(None): return None,None,None, True 
        self.hyp_in_queue = h 

        node_res_seq = self.next_hypothesis_and_resdist_on_action(df,h,dag)

        # case: reached end of action graph 
        if type(node_res_seq) == type(None): 
            return None,None,None,False   

        # choose a question to ask 
        q = self.choose_question() 

        ## NOTE: code was added here so that 
        ##      automaton terminates when Q is 
        ##      fully certain of its answers. 
        #if type(q) == type(None): 
        #    self.fin_stat = True    
        self.q_idn = q 

        # load next node into queue 
        self.p_next_node = node_res_seq[0][0] 

        self.num_hyp_deltas += 1 
        return deepcopy(h),node_res_seq,q,False 

    def choose_question(self): 
        q0,q1 = self.hs_hyp_mach.active_questions()
        q0,q1 = sorted(q0),sorted(q1)

        # if there are any unanswered questions, choose 
        # one of them 
        if len(q0) > 0: 
            q0 = prg_seqsort(q0,self.prg)
            i = int(self.prg()) % len(q0) 
            return q0[i] 

        # case: all questions have been answered, and 
        #       all answers have been marked as certain. 
        if len(q1) == 0: 
            return None 

        # choose arbitrary question that has already been answered 
        q1 = prg_seqsort(q1,self.prg)
        i = int(self.prg()) % len(q1) 
        return q1[i] 

    def next_hyp(self): 
        self.reset_hyp_delta_vars() 

        if self.fin_iter_stat: 
            return None 

        if self.hyp_index >= len(self.act_hyp): 
            self.fin_iter_stat = True 
            return None 

        q = self.act_hyp[self.hyp_index] 
        self.hyp_index += 1 
        return q 

    """
    predicts the next node (after the tail of `hyp`). 
    """
    def hyp_delta(self,df:DAGTraversalFunctionTypeHSD,hyp:NodePath,\
        dag:DAGraphContainer):
        assert type(df) == DAGTraversalFunctionTypeHSD
        assert type(hyp) == NodePath  
        assert issubclass(type(dag),DAGraphContainer)

        M = self.current_hidden_state_hyp()
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

        predicted_next = self.hyp_delta(df,hyp,dag) 
        if type(predicted_next) == type(None): 
            return None 

        C = dag.children_of_node(hyp.tail())

        if len(C) < 2: 
            return [(predicted_next,1.0)]


        # NOTE: partitioning scheme is wonky here 
        prt = prg_partition_for_float(49,len(C) - 1,prg__single_to_int(self.prg),0.5,500)
        prt = prt / 100. 

        C_ = sorted(C - {predicted_next}) 
        S = [(predicted_next,0.51)]

        for p,c in zip(prt,C_): 
            S.append((c,p))

        return S 

    #-------------------------------------- methods to reset variables that operate in questioning process

    """
    method called after all hypotheses have been iterated through 
    by the False Question Type SP automaton. 
    """
    def reset_iter(self): 
        self.hyp_index = 0 
        self.fin_iter_stat = False 
        self.tail2fb_map.clear() 
        self.num_hyp_deltas = 0 

    def reset_hyp_delta_vars(self): 
        self.hyp_in_queue = None 
        self.p_next_node = None 
        self.lfeedback = None 
        self.cfeedback = None 
        self.q_idn = None 
        self.tmp_s2l2c_map.clear() 

        for c in self.hs_hyp_mach.state_set: 
            self.tmp_s2l2c_map[c] = defaultdict(int) 

    #-----------------------------------------  receiving feedback from subject: probable labelsets of hidden state
    #-----------------------------------------  and context on actions. 

    def recv_feedback(self,lfeedback,cfeedback): 
        assert type(lfeedback) in {type(None),bool}
        assert type(cfeedback) in {type(None),bool}

        self.lfeedback = lfeedback 
        self.cfeedback = cfeedback
        self.tail2fb_map[self.p_next_node] = (self.lfeedback,self.cfeedback)

    """
    processes a <NodePath> from subject, into the 
    appropriate categories and labels. 
    """
    def recv_probable_secret(self,M): 
        assert type(M) == dict 

        for state,labelset in M.items():  
            for l in labelset: 
                if l not in self.tmp_s2l2c_map[state]: 
                    self.tmp_s2l2c_map[state][l] = 0 
                self.tmp_s2l2c_map[state][l] += 1 

    """
    concluding step after posing hypothesis question 
    """
    def h_conclusion(self): 
        # case: certainty of most dominant being correct and questions remaining 
        if self.cfeedback == True and type(self.q_idn) != type(None): 
            l2v = self.tmp_s2l2c_map[self.q_idn]
            l2v_ = [(k,v) for k,v in l2v.items()]
            lset = min_or_max_rank_in_sequence(l2v_,vf=lambda x:x[1],is_min_rank=False)
            lset = set([l[0] for l in lset]) 
            self.hs_hyp_mach.set_certain_category(self.q_idn,lset) 

        # add frequencies in cache to `hs_hyp_mach`
        for c,f in self.tmp_s2l2c_map.items():
            self.hs_hyp_mach.add_frequencies_to_category(c,f) 
        self.hs_hyp_mach.update_induction() 

        # update path and add it back to memory 
        ##self.act_hyp.delete_path(self.hyp_in_queue) 

        w = 0 
        # case: location feedback outputs True -> mark node as relevant 
        if self.lfeedback == True: 
            w = 1 

        P = self.act_hyp.update_path(deepcopy(self.hyp_in_queue),self.p_next_node,w)
        return self.act_hyp.add_path_to_mem(P,self.prg)