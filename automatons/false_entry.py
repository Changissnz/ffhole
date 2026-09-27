from .false_entry_agents import * 
from morebs2.numerical_generator import modulo_in_range,prg__single_to_int

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

        self.agents = dict() 
        self.max_active_agents = max_active_agents 
        self.max_agents = max_agents 
        self.tstep_inaccuracy = tstep_inaccuracy

        self.acount = 0 

        self.passed = set() 
        self.terminated = set() 
        return

    def exec(self): 
        self.exec_phase_1() 
        self.exec_phase_2()

    #---------------------------------- spawning new agents 

    def generate_hyp_for_agent(self): 
        q = sorted(self.surface.entry_points)
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
        if d <= 0: return 

        i = modulo_in_range(int(self.prg()),[1,d + 1]) 

        for _ in range(i): 
            hyp = self.generate_hyp_for_agent() 
            a = self.spawn.spawn_from_hyp(hyp)
            self.agents[a.idn] = a 
            self.acount += 1 

    #----------------------------------- transmitting agent weight-range hypotheses to <FESurface> 

    def exec_agent_wr_hyp(self): 
        M = {}
        for idn,a in self.agents.items(): 
            a.set_next_weight_range() 
            M[idn] = deepcopy(a.next_wr) 
        return M 

    def transmit_agent_wr_hyp_to_surface(self): 
        M = self.exec_agent_wr_hyp() 
        self.surface.load_agent_hyp_map(M) 
        return

    def exec_surface_appearance(self): 
        self.surface.project_appearance() 
        return 

    def exec_phase_1(self): 
        self.allow_spawn() 
        self.transmit_agent_wr_hyp_to_surface() 
        self.exec_surface_appearance() 


    #---------------------------------- agents make moves and surface executes traps

    def agent_decision_(self,idn): 
        A = self.agents[idn] 
        loc = A.node_loc 

        q = self.surface.agent_location_to_appeared_node_weights(loc) 
        x = A.choose_next_loc(q) 
        return x 

    def exec_agent_decisions(self): 
        agent_idns = sorted(self.agents.keys())
        decisions = {} 
        for k in agent_idns: 
            decisions[k] = self.agent_decision_(k)
        print("decisions")
        print(decisions)
        return decisions 

    def exec_phase_2(self):
        d = self.exec_agent_decisions() 
        self.surface.update_agent_locations(d) 
        terminated_agents = self.surface.remove_trapped_agents()
        print("TERMINATED")
        print(terminated_agents) 
        for t in terminated_agents: 
            del self.agents[t] 
        
        self.terminated |= terminated_agents

        passed = self.surface.passed_agents()
        for p in passed: del self.agents[p] 
        self.passed |= passed 