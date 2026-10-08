from .incompetent_agents import * 

# NOTE: used specifically for False Incompetency 
def summarize_boolean_action_map(idn_to_boolvec,selected_indices): 

    bools = [] 
    for i in selected_indices:
        c = 0  
        for v in idn_to_boolvec.values(): 
            c += int(v[i]) 

        bools.append((c / len(idn_to_boolvec)) >= 0.5)
    return bools  

"""
Automaton that acts as an environment for the activity of two classes of agents:
(I) a `demander` <FIDemander>; `demander` demands a group of k agents to demonstrate 
    its competence in executing tasks, formatted as a vector V_i of iterations. 
(II) a group of k agents, <IncompetentAgentGroupTypeDEGD>. Agents demonstrate and 
     execute actions according to the demands (number of iterations) given to them 
     by the `demander`.

This procedure is used for False Incompetency. 

- the `demander` demands every agent of `igroup` to demonstrate its actions over k 
  iterations. 
- `demander` receives a map with information on that demonstration, 
    agent idn -> matrix of shape (2,k), 
        [0] contradiction mode, {-1,0,1,2},
        [1] uncertainty towards observer (the `demander`), [0.,1.] 
- `demander` determines the subset of indices I of those k iterations would yield 
   executive actions from `igroup` that output TRUE, by majority vote. 

    **Demander objective** 
Objective is for demander to select the executive actions A such that 
    COUNT(A,true) - COUNT(A,false) 
is the greatest possible given V_i, the vector of number of iterations per 
demand. 

NOTE: see file<automatons.incompetent_agents> for the mathematics behind this 
decision-making. 
"""
class FalseIncompetency:

    def __init__(self,demander:FIDemander,igroup:IncompetentAgentGroupTypeDEGD): 
        assert type(demander) == FIDemander
        assert type(igroup) == IncompetentAgentGroupTypeDEGD

        self.demander = demander 
        self.igroup = igroup 

        self.di_index = 0
        self.fin_stat = False  

        self.results = Counter([])
        return 

    """
    main method
    """ 
    def exec_next_demand(self):
        if self.fin_stat == True: 
            return 

        if self.di_index >= len(self.demander.demand_iterations_seq):
            self.fin_stat = True 
            return 

        D = self.demander.demand_iterations_seq[self.di_index] 

        # execute demonstration 
        ext_prg = self.demander.prg 
        M = self.igroup.demonstrate(D,ext_prg) 

        #   demander receives demo results 
        self.demander.recv_demonstration_dict(M)
        M2 = self.igroup.demo_results() 
        I = self.demander.calculate_accept_indices(M2)

        # process demander selection of agent results 
        R = self.igroup.execute()
        results = summarize_boolean_action_map(R,I)

        # add to cumulative results 
        c = Counter(results) 
        self.results += c 
        self.di_index += 1 

    def score(self): 
        return self.results[True] - self.results[False] 