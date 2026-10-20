from .false_question_agents import * 

"""
False Question Type (D)elay and (D)ivert. 
"""
class FalseQuestionTypeDD: 

    def __init__(self,Q:QuestionTypeSWPS,fs:FQSubjectTypeDD,fas:FQSwarmAgent,\
        subject_objective:ObjectiveTypeUSGMP,verbose=True): 
        assert type(Q) == QuestionTypeSWPS
        assert type(fs) == FQSubjectTypeDD
        assert type(fas) == FQAgentSwarm
        assert type(subject_objective) == ObjectiveTypeEFIT

        self.Q = Q 
        self.fs = fs
        self.fas = fas 
        self.subject_objective = subject_objective
        self.verbose = verbose 

        self.queue_pass_proc = deque() 
        self.queue_proof_proc = deque() 
        return 


    """
    main method
    """
    def exec_q_round(self): 
        self.fas.agent_action_ctr_map.clear() 
        self.start_q_chain() 

        while len(self.queue_pass_proc) > 0 or len(self.queue_proof_proc) > 0: 
            self.exec_q_round_() 

    """
    starts the questioning round 
    """
    def start_q_chain(self): 

        A = self.fas.first_q_agent()
        self.exec_q(A,self.fs) 
        return

    """
    runs the questioning round after it has started. Every call 
    executes one proof process between questioning and answering 
    agents, and one pass process from the previous questioning agent 
    to its neighbors. 
    """
    def exec_q_round_(self): 
        # next proof 
        if len(self.queue_proof_proc) > 0: 
            x = self.queue_proof_proc.popleft() 

            A0 = self.idn_to_agent(x[0]) 
            A1 = self.idn_to_agent(x[1]) 
            self.exec_proof(A0,A1)  

        # next pass (bfs-order) 
        if len(self.queue_pass_proc) > 0: 
            q = self.queue_pass_proc.popleft() 
            for q_ in q: 
                A0,A1 = self.idn_to_agent(q_[0]),self.idn_to_agent(q_[1]) 
                self.exec_pass(A0,A1) 
        
        if self.verbose: 
            print("==================================")
        return 

    """
    executes question action from `q_agent` to `a_agent` 
    """
    def exec_q(self,q_agent,a_agent): 

        # pass answer 
        stat = a_agent == self.fs
        if stat: 
            ans = a_agent.answer(q_agent.idn)  
        else: 
            ans = a_agent.answer() 

        q_agent.recv_answer(ans,stat) 
        self.fas.update_action_ctr(q_agent.idn) 

        # questioning agent makes decision 
        D = q_agent.decision_0()

        if self.verbose: 
            s0,s1 = self.agent_to_idn(q_agent),self.agent_to_idn(a_agent) 
            print("q={},a={} --> q {}".format(s0,s1,D)) 

        # proof demanded; questioning agent requires one from both the sender 
        # Swarm Agent and the Subject. 
        if D == "proof":
            self.enqueue_proof_proc(q_agent,self.fs) 
            if self.agent_to_idn(a_agent) != "subject": 
                self.enqueue_proof_proc(q_agent,a_agent) 
        else: 
            self.enqueue_pass_proc(q_agent)
        return 

    """
    Agent `q_agent` demands `a_agent` prove its answer. 
    Process occurs via <ProofDifferentialSimulatorTypeACSGT>. 
    """ 
    def exec_proof(self,q_agent,a_agent): 
        prg0 = a_agent.prg 
        prg1 = q_agent.prg   
        pf,score,autocorrect_ratio = self.Q.proof_process(prg0,prg1)

        a_agent.update_error_term(autocorrect_ratio) 
        
        D2 = q_agent.decision_p(pf,score) 
        if self.verbose: 
            print("-- {} provides proof to {}".format(self.agent_to_idn(a_agent),self.agent_to_idn(q_agent))) 
            print("-- proof decision: {}, score: {}   {}".format(D2,score,autocorrect_ratio))

        # case: subject is answering agent
        if a_agent == self.fs:
            a_agent.num_queries += 1 
            a_agent.update_ar_count(D2 == "accept") 
            # subject changes its answer to a_agent 
            if D2 == "reject":  
                a_agent.update_answer(q_agent.idn,q_agent.current_answer,"exp") 
            # subject updates its most recent answer sent to agent 
            a_agent.update_answer(q_agent.idn,q_agent.received_answer,"sent")
        
        self.fas.update_action_ctr(q_agent.idn) 
        self.enqueue_pass_proc(q_agent)

    def exec_pass(self,s_agent,r_agent): 
        self.exec_q(r_agent,s_agent)
        return 

    #------------------------ queue update methods 

    def enqueue_proof_proc(self,q_agent,a_agent): 

        idn0 = self.agent_to_idn(q_agent)
        idn1 = self.agent_to_idn(a_agent) 

        if self.verbose: 
            print("[!] {} demands proof from {}".format(idn0,idn1))

        self.queue_proof_proc.append((idn0,idn1)) 

    def enqueue_pass_proc(self,q_agent): 
        neighbors = self.fas.active_neighbor_agents(q_agent.idn) 
        neighbors = prg_seqsort(sorted(neighbors),self.fas.collective_prg)

        if self.verbose: 
            print("{} passes to neighbors: {}".format(self.agent_to_idn(q_agent),neighbors)) 

        X = [] 
        for n in neighbors: 
            X.append((q_agent.idn,n)) 
        self.queue_pass_proc.append(X) 
        return 

    def idn_to_agent(self,idn): 
        if idn == "subject": return self.fs 
        return self.fas.idn_to_agent(idn) 

    def agent_to_idn(self,a_agent): 
        return "subject" if type(a_agent) == FQSubjectTypeDD else \
            a_agent.idn

    #------------------------------------------ performance measures 

    def error_terms(self): 
        D = self.fas.error_terms() 
        D["subject"] = self.fs.error_term
        return D 

    def inconsistencies(self): 
        M = self.fas.inconsistency_map() 
        M0 = self.fs.incon_func.inconsistency_count
        return M0,M 
