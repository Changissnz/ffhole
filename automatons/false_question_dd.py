
"""
False Question Type (D)elay and (D)ivert. 
"""
class FalseQuestionTypeDD: 

    def __init__(self,Q:QuestionTypeSWPS,fs:FQSubjectTypeDD,fsa:FQSwarmAgent,subject_objective:ObjectiveTypeUSGMP): 
        assert type(Q) == QuestionTypeSWPS
        assert type(fs) == FQSubjectTypeDD
        assert type(fsa) == FQSwarmAgent
        assert type(subject_objective) == ObjectiveTypeUSGMP

        self.Q = Q 
        self.fs = FQSubjectTypeDD
        self.fsa = FQSwarmAgent 
        self.subject_objective = subject_objective

        self.queue_pass_proc = deque() 
        self.queue_proof_proc = deque() 
        return 

    def exec_q_round(self): 
        return -1 

    def idn_of_agent(self): 
        return -1 

    def exec_action(self,q_agent,a_agent): 

        # pass answer 
        ans = a_agent.answer(q_agent.idn)  
        q_agent.recv_answer(ans) 

        D = q_agent.decision()

        # 
        if D == "proof":
            self.exec_proof(q_agent,a_agent)
        return -1  

    def exec_proof(self,q_agent,a_agent): 
        prg0 = a_agent.prg 
        prg1 = q_agent.prg   
        pf,score,autocorrect_ratio = self.Q.proof_process(prg0,prg1)

        a_agent.update_error_term(autocorrect_ratio) 
        
        D2 = q_agent.decision_p(pf,score) 

        # case: subject is answering agent
        if a_agent == self.fs:
            # subject changes its answer to a_agent 
            if D2 == "reject":  
                a_agent.update_answer(q_agent.idn,q_agent.current_answer,"exp") 
            # subject updates its most recent answer sent to agent 
            a_agent.update_answer(q.agent.idn,ans,"sent")
