from .false_question_agents import * 

"""
False Question Type (D)elay and (D)ivert. 
"""
class FalseQuestionTypeDD: 

    def __init__(self,Q:QuestionTypeSWPS,fs:FQSubjectTypeDD,fas:FQSwarmAgent,subject_objective:ObjectiveTypeUSGMP): 
        assert type(Q) == QuestionTypeSWPS
        assert type(fs) == FQSubjectTypeDD
        assert type(fas) == FQAgentSwarm
        assert type(subject_objective) == ObjectiveTypeUSGMP

        self.Q = Q 
        self.fs = fs
        self.fas = fas 
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
        print("A_AGENT: ",a_agent) 
        stat = a_agent == self.fs
        if stat: 
            ans = a_agent.answer(q_agent.idn)  
        else: 
            ans = a_agent.answer() 

        q_agent.recv_answer(ans,stat) 

        D = q_agent.decision_0()

        # 
        if D == "proof":
            self.exec_proof(q_agent,a_agent)
        return 

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
            a_agent.update_answer(q_agent.idn,q_agent.received_answer,"sent")
