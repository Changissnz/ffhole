from .false_question_agents_sp import * 
from morebs2.numerical_generator import prg_to_LCG_stack
from operator import sub 

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
        return 

    def preproc(self): 
        self.subject.first_move(self.action_graph)
        return

    def __next__(self): 

        # have `Q` predict the next node that `subject` travels to, for 
        # every one of its hypotheses. 
        
        return -1  

    def process_hyp(self): 
        return 

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