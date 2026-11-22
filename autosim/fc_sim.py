from automatons.false_claim_i import * 


def FCTI_prng_assignment_function_(agent_idn:str): 
    
    def f(fci:FalseClaimTypeI,prg):
        assert type(fci) == FalseClaimTypeI
        fci.set_prg(agent_idn,prg)
        return 

    return f 

def FCTI_env_mode_shift_function(fci:FalseClaimTypeI): 
    return None 

def FCTI_env_solution_fetch_function_(agent_idn:str): 
    assert agent_idn in {"subject","claimant"}
    
    def f(fci:FalseClaimTypeI): 
        if agent_idn == "subject": 
            return fci.subject.cumulative_instability
        return fci.claimant.cumulative_instability
    
    return f

def FCTI_env_cmp_solution_(agent_idn:str): 

    def f(fci:FalseClaimTypeI,fci2:FalseClaimTypeI): 
        s1 = FCTI_env_solution_fetch_function_(agent_idn)(fci)
        s2 = FCTI_env_solution_fetch_function_(agent_idn)(fci2)
        return s1 < s2

    return f 

def FCTI_env_run_(num_iter):

    def f(fci:FalseClaimTypeI):
        for _ in range(num_iter): 
            next(fci) 
    
    return f 