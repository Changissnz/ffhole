from .false_question_agents_sp import * 
from morebs2.numerical_generator import prg_to_LCG_stack
from operator import sub 

# NOTE: first draft 
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
        return 

    def preproc(self): 
        self.subject.first_move(self.action_graph)
        self.Q.act_hyp.load_starting_nodes(deepcopy(self.action_graph.l2n_map[0]))

        return

    def __next__(self): 

        if self.fin_stat: return 

        # have `Q` predict the next node that `subject` travels to, for 
        # every one of its hypotheses. 
        stat1 = self.process_Q_hypotheses() 
        self.Q.increment_timestamp()

        # have `subject` make its action on action graph 
        stat2 = self.subject.next_action(self.action_graph,self.action_graph_op)

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
        return len(self.Q.act_hyp) == 0 

    def process_one_hyp(self): 

        h,node_res_seq,q,fin_stat  = self.Q.process_next_hyp(self.action_graph_op,self.action_graph)

        # case: finished 
        if fin_stat: 
            self.Q.act_hyp.flush_queue() 
            return None 

        # case: hypothesis reached end of actions 
        if type(h) == type(None): 
            return True 

        # case: all questions have been answered and answers marked for certainty
        if type(q) == type(None): 
            self.Q.act_hyp.flush_queue() 
            return None 

        # transmit Q's query to subject 
        q_hs_hyp = self.Q.current_hidden_state_hyp()

        # subject responds to Q's query 
        lfeedback,cfeedback = self.subject.respond_to_Q_hyp(q,self.action_graph,\
            self.action_graph_op,h.tail(),node_res_seq,q_hs_hyp)

        self.Q.recv_lfeedback(lfeedback,cfeedback)

        p_response = self.subject.paths_for_response() 

        for p in p_response: 
            M = nodepath_to_s2l_map(self.subject.de_secret.dag,p)
            self.Q.recv_probable_secret(M) 
        return self.Q.h_conclusion() 

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