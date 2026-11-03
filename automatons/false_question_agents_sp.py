from falses.bi_dag_function import * 
from falses.hyp_container_gp import * 

class FQSubjectTypeSP: 

    def __init__(self,de_secret:SecretSpaceTypeDAG): 
        assert type(de_secret) == SecretSpaceTypeDAG
        self.de_secret = de_secret
        return 

class FQQuestionerTypeSP: 

    def __init__(self,category_set:set,initial_hs_hyp,prg):  

        assert type(prg) in {MethodType,FunctionType}

        # used for hypotheses on subject's activity 
        self.act_hyp = HypothesisContainerTypeGP()

        # used for Hidden State hypotheses
        self.hs_hyp_mach = StateInductionTypeMFUC(category_set)

        self.prg = prg   
        return 

    def update_hs_hyp(self): 
        return -1 

    def next_hypothesis_on_action(self,hyp:NodePath):
        assert type(hyp) == NodePath 
        assert type(possible_next) == set 
        return -1  
    
