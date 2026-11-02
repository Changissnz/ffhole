from .false_question_agents_sp import * 


class FalseQuestionTypeSP: 

    def __init__(self,Q:FQQuestionerTypeSP,subject:FQSubjectTypeSP,action_graph:DAGraphContainer): 
        assert type(Q) == FQQuestionerTypeSP
        assert type(subject) == FQSubjectTypeSP
        assert type(action_graph) == DAGraphContainer

        self.Q = Q 
        self.subject = subject 
        self.action_graph = action_graph 
        return 

    def __next__(self): 

        return -1  