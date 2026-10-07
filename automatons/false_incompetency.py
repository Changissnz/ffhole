from .incompetent_agents import * 

# NOTE: used specifically for False Incompetency 
def summarize_boolean_action_map(idn_to_boolvec,selected_indices): 

    bools = [] 
    for i in selected_indices:
        c = 0  
        for v in idn_to_boolvec.values(): 
            c += int(v[i]) 

        bools.append(c / len(idn_to_boolvec))
    return bools  

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
        c = Counter(results) 
        self.results += c 
