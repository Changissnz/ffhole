from .false_entry_agents import * 

class FalseEntry: 

    def __init__(self,surface:FESurface,agent_spawn:FEAgentSpawn,prg,max_active_agents:int,max_agents:int,\
        tstep_inaccuracy:float):  
        
        assert type(surface) == FESurface 
        assert type(agent_spawn) == FEAgentSpawn
        assert agent_spawn.end_points == surface.end_points
        assert type(max_active_agents) == int and max_active_agents > 0 
        assert max_active_agents <= max_agents 
        assert 0 <= tstep_inaccuracy <= 1.0 

        self.surface = surface 
        self.spawn = agent_spawn 
        self.prg = prg 

        self.agents = [] 
        self.max_active_agents = max_active_agents 
        self.max_agents = max_agents 
        self.tstep_inaccuracy = tstep_inaccuracy

        self.acount = 0 
        return

    #---------------------------------- spawning new agents 

    def generate_hyp_for_agent(self): 
        q = sorted(entry_points)
        i = int(self.prg()) % len(q) 

        entry = q[i] 

        return self.surface.prg_choose_weight_range_hypothesis_for_entry(entry,self.spawn.hyp_type,self.tstep_inaccuracy)

    def allow_spawn(self): 
        # case: max number of agents reached
        if self.acount >= self.max_agents: 
            return 

        # case: spawn 
        d0 = self.max_active_agents - len(self.agents)
        d1 = self.max_agents - len(self.agents) 
        d = min([d0,d1]) 
        i = modulo_in_range(prg__single_to_int(self.prg),[1,d + 1]) 

        for _ in range(i): 
            hyp = self.generate_hyp_for_agent() 
            a = self.spawn.spawn_from_hyp(hyp)
            self.agents.append(a) 

    def transmit_agent_wr_hyp_to_surface(self): 
        return -1 

    def exec_surface_appearance(self): 
        return -1 